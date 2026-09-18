"""Read display formats without turning formatted text into financial inputs."""
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP, localcontext
import math
import re
from xml.etree import ElementTree as ET
from .vendor import input_engine as core

BUILTIN={0:'General',1:'0',2:'0.00',3:'#,##0',4:'#,##0.00',9:'0%',10:'0.00%',
         11:'0.00E+00',14:'mm-dd-yy',15:'d-mmm-yy',16:'d-mmm',17:'mmm-yy',
         18:'h:mm AM/PM',19:'h:mm:ss AM/PM',20:'h:mm',21:'h:mm:ss',22:'m/d/yy h:mm',49:'@',
         5:'#,##0;(#,##0)',6:'#,##0;[Red](#,##0)',7:'#,##0.00;(#,##0.00)',8:'#,##0.00;[Red](#,##0.00)',
         37:'#,##0;(#,##0)',38:'#,##0;[Red](#,##0)',39:'#,##0.00;(#,##0.00)',40:'#,##0.00;[Red](#,##0.00)',
         41:'#,##0;(#,##0)',42:'#,##0;(#,##0)',43:'#,##0.00;(#,##0.00)',44:'#,##0.00;(#,##0.00)',
         45:'mm:ss',46:'[h]:mm:ss',47:'mmss.0',48:'##0.0E+0'}
# Built-in currency symbols depend on Excel's locale. Only an explicit symbol
# in the workbook format is displayed; the grid never invents a currency.


def _duration_display(value, code):
    """Only the three exact built-in duration formats, not a format parser."""
    if value < 0:
        # Negative serial times depend on Excel's date system. Keep their raw
        # value instead of presenting an invented clock time as a valid result.
        return str(value)
    factor = 10 if code == 'mmss.0' else 1
    ticks = int((Decimal(str(value)) * 86400 * factor).to_integral_value(rounding=ROUND_HALF_UP))
    seconds, fraction = divmod(ticks, factor)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if code == '[h]:mm:ss':
        return f'{hours}:{minutes:02d}:{seconds:02d}'
    if code == 'mmss.0':
        return f'{minutes:02d}{seconds:02d},{fraction}'
    return f'{minutes:02d}:{seconds:02d}'


def _scientific_display(value, code):
    """Built-in 11 (scientific) and 48 (engineering), including carry rounding."""
    engineering = code == '##0.0e+0'
    step, precision, exponent_width = (3, 1, 1) if engineering else (1, 2, 2)
    with localcontext() as context:
        context.prec = 34
        number = Decimal(str(value))
        exponent = number.copy_abs().adjusted() // step * step if number else 0
        mantissa = number.scaleb(-exponent).quantize(Decimal(1).scaleb(-precision), rounding=ROUND_HALF_UP)
        if abs(mantissa) >= 10 ** step:
            exponent += step
            mantissa = mantissa.scaleb(-step)
        text = f'{mantissa:.{precision}f}'.replace('.', ',')
        return f'{text}E{"+" if exponent >= 0 else "-"}{abs(exponent):0{exponent_width}d}'


def cell_display(wb,sheet,address):
    cell=wb.sheet(sheet)[1].get(address)
    value=wb.value(sheet,address)
    if not hasattr(wb,'_web_number_formats'):
        styles=ET.fromstring(wb.z.read('xl/styles.xml'))
        wb._web_number_formats={**BUILTIN,**{int(x.get('numFmtId')):x.get('formatCode','General') for x in styles.findall('m:numFmts/m:numFmt',core.N)}}
    index=int(cell.get('s','0')) if cell is not None else 0
    style=wb.xfs[index]
    code=wb._web_number_formats.get(int(style.get('numFmtId','0')),'General')
    display='' if value is None else str(value)
    if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value):
        section=code.split(';')[0]
        clean=re.sub(r'"[^"]*"|\[[^]]*\]|\\.','',section).lower()
        if code.lower() in ('mm:ss','[h]:mm:ss','mmss.0'):
            display=_duration_display(value,code.lower())
        elif code.lower() in ('0.00e+00','##0.0e+0'):
            display=_scientific_display(value,code.lower())
        elif any(mark in clean for mark in ('yy','dd','jj','aaaa')):
            if wb.date1904 or value>=61:
                base=dt.datetime(1904,1,1) if wb.date1904 else dt.datetime(1899,12,30)
                try:
                    date=base+dt.timedelta(days=value)
                    display=date.strftime('%d/%m/%Y' + (' %H:%M' if 'h' in clean else ''))
                except (OverflowError,ValueError):
                    pass
        elif code!='General' and code!='@':
            precision=min(10,len(re.search(r'\.([0#]+)',clean).group(1))) if re.search(r'\.([0#]+)',clean) else 0
            scaled=value*100 if '%' in clean else value
            # Only a comma between numeric placeholders requests grouping.
            # Quoted/escaped commas and trailing scaling commas do not.
            grouping=',' if re.search(r'[0#?],[0#?]',clean.split('.')[0]) else ''
            display=f'{scaled:{grouping}.{precision}f}'.replace(',','\u202f').replace('.',',')
            if '%' in clean:
                display+=' %'
            if '€' in section:
                display+=' €'
            if value<0 and len(code.split(';'))>1 and '(' in code.split(';')[1]:
                display='('+display.lstrip('-')+')'
    if isinstance(value,bool):
        display='VRAI' if value else 'FAUX'
    return {'display':display,'format':code}
