"""Retain the existing input/date/business contracts in structural drafts."""
from copy import deepcopy
from .vendor import input_engine as core
from .web_model_profile import map_location,LogicalWorkbook
from .web_structure import plan_operations


def prepare_native_operations(engine,source,profile,operations):
    actual=core.Workbook(source)
    logical=LogicalWorkbook(actual,profile)
    from .web_model import _logical_schema
    schema=_logical_schema(profile,engine.schema)
    updates=[]
    from .web_blocks import expand_operations, ExpandedOperations
    operations=expand_operations(operations)
    normalized=ExpandedOperations(envelope_count=operations.envelope_count,contains_blocks=operations.contains_blocks)
    current=profile
    class InputView:
        date1904=actual.date1904
        def value(self,sheet,cell):
            for update in reversed(updates):
                if (update['sheet'],update['cell'])==(sheet,cell):
                    return core.excel_serial(update['value'],self.date1904) if update['kind']=='date' and update['value'] is not None else update['value']
            return logical.value(sheet,cell)
        def formula(self,sheet,cell):
            return None if any((u['sheet'],u['cell'])==(sheet,cell) for u in updates) else logical.formula(sheet,cell)
        def snapshot(self,sheet,cell):
            return {'value':self.value(sheet,cell),'formula':self.formula(sheet,cell)}
        def fill(self,sheet,cell):
            mapped=map_location(profile,sheet,cell)
            return actual.fill(mapped['sheet'],mapped['cell']) if mapped else None
    view=InputView()
    try:
        for original in operations:
            operation=deepcopy(original)
            if operation['type']=='set_value':
                owner=map_location(current,operation['sheet'],operation['cell'],reverse=True)
                spec=schema['cells'].get(owner['sheet'],{}).get(owner['cell']) if owner else None
                if spec is not None:
                    sheet,cell=owner['sheet'],owner['cell']
                    # Equivalent formula spelling follows current Excel references.
                    physical=map_location(profile,sheet,cell)
                    current_spec=engine.schema['cells'].get(physical['sheet'],{}).get(physical['cell'],{}) if physical else {}
                    if 'default_formula' in current_spec:
                        spec['default_formula']=current_spec['default_formula']
                    spec['fill']=view.fill(sheet,cell)
                    change=core.normalize_change(view,schema,{'sheet':sheet,'cell':cell,'value':operation['value'],
                        'reason':operation.get('reason') or 'Modification explicite du brouillon web',
                        'expected':view.snapshot(sheet,cell),'replace_existing':True,'override_default':True,
                        'evidence':operation.get('evidence_id')})
                    updates.append(change)
                    if change['kind']=='date' and change['value'] is not None:
                        operation['value']=core.excel_serial(change['value'],actual.date1904)
            normalized.append(operation)
            if operation['type'] not in ('set_value','set_formula'):
                _,current=plan_operations(current,[operation])
        if updates and 'Control' in schema.get('cells',{}):
            from .decision_offers import business_checks
            business_checks(profile,logical,schema,updates)
            for update in updates:
                if (update['sheet'],update['cell'])==('Control','C10') and update['value'] is not None and not update['value'].endswith('-01-01'):
                    raise ValueError('La date de début doit être le 1er janvier.')
        return normalized
    finally:
        actual.close()
