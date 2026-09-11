"""Preuves générées de la revue sémantique ; outil interne : tools/build_field_semantic_basis.py."""
import json

BASIS = json.loads(r'''{
  "version": "tca-bp-field-semantics/1.0.0",
  "template_sha256": "e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12",
  "schema_sha256": "f0da6d7da5df3fda899adc23ec33b5d40f413821481dced7a11f46d78d8867eb",
  "fields": {
    "inflation_general": {
      "shape_sha256": "155a0a7c47e773a8c9e31e49afe2e3a7cfd604e6d97c19a4ff6637b0a01158dd",
      "source_label": "Inflation générale annuelle",
      "default_sources": {}
    },
    "inflation_price": {
      "shape_sha256": "f24978a65001f64ec14885ffe892e3bbc1647a0d369293da338605cad58b52b9",
      "source_label": "Indexation annuelle des prix de vente",
      "default_sources": {}
    },
    "industrial_receivable_days": {
      "shape_sha256": "690feff2e6f1d84ef13b96f1cd0d8f1d60170031948b1dcd5983a85e9eb6f62e",
      "source_label": "Délai clients industriels de référence",
      "default_sources": {}
    },
    "transformation_cost_reduction": {
      "shape_sha256": "eddae5daa0c54fc8daec3100278e62be78b7de4abd8206075313de6a10d6a84d",
      "source_label": "Réduction annuelle des coûts directs de transformation",
      "default_sources": {}
    },
    "inflation_salary": {
      "shape_sha256": "e46523b5592a51be6c9eae14bf9107f1d3ee83b32f9c6c411b574e858e1dc488",
      "source_label": "Inflation salariale annuelle",
      "default_sources": {}
    },
    "employer_charge_reference": {
      "shape_sha256": "0e9d03b770306232527bd1011cba08d0e14ba0b5719c7f3220207f4e085a7824",
      "source_label": "Taux indicatif de charges patronales",
      "default_sources": {}
    },
    "headcount_target": {
      "shape_sha256": "8cf0d84ee3ae889ada9f72d344e09a280da5c4065077111cd58f50348d7c7f43",
      "source_label": "Effectif cible à terme du plan",
      "default_sources": {}
    },
    "opening_cash": {
      "shape_sha256": "01945c7c0d9cac94764428654f3e47d578887ab510efd06359cfebaee461e624",
      "source_label": "Trésorerie d’ouverture du modèle",
      "default_sources": {}
    },
    "offer_label": {
      "shape_sha256": "7afafe94e6ab10c231f996117021ee2935a27762fae5332512c0590170f2427d",
      "source_label": "Libellé de l’offre",
      "default_sources": {}
    },
    "offer_active": {
      "shape_sha256": "96a5b0ea0f33fbb2c0ac380e96e45245cf2ce686fd0f057b35c4f3d78d14e760",
      "source_label": "Offre active",
      "default_sources": {}
    },
    "offer_unit": {
      "shape_sha256": "7cbde009384e4b01dffe31c88db865c97fa50f8e457818ecffe35c5285acf981",
      "source_label": "Unité",
      "default_sources": {}
    },
    "offer_in_revenue": {
      "shape_sha256": "aea772901dff2d41357235a75e123b35bfb442289687cc8191b74829576b2ec7",
      "source_label": "Inclure au chiffre d’affaires",
      "default_sources": {}
    },
    "offer_price_2026": {
      "shape_sha256": "0fcf4087583f811154f1c00004a66800ff7dfb29ef7a4f373038c598f42b6977",
      "source_label": "Prix de vente A1",
      "default_sources": {}
    },
    "offer_price_2027_2030": {
      "shape_sha256": "1d8dea5e4c004ce56df699356a1651e56cbf7e6db847d28450c7bd5d32f23f00",
      "source_label": "Prix de vente A2–A5",
      "default_sources": {
        "G15": {
          "formula": "F15*(1+$D$5)",
          "references": [
            "'Assumptions'!F15",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H15": {
          "formula": "G15*(1+$D$5)",
          "references": [
            "'Assumptions'!G15",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I15": {
          "formula": "H15*(1+$D$5)",
          "references": [
            "'Assumptions'!H15",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J15": {
          "formula": "I15*(1+$D$5)",
          "references": [
            "'Assumptions'!I15",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G16": {
          "formula": "F16*(1+$D$5)",
          "references": [
            "'Assumptions'!F16",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H16": {
          "formula": "G16*(1+$D$5)",
          "references": [
            "'Assumptions'!G16",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I16": {
          "formula": "H16*(1+$D$5)",
          "references": [
            "'Assumptions'!H16",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J16": {
          "formula": "I16*(1+$D$5)",
          "references": [
            "'Assumptions'!I16",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G17": {
          "formula": "F17*(1+$D$5)",
          "references": [
            "'Assumptions'!F17",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H17": {
          "formula": "G17*(1+$D$5)",
          "references": [
            "'Assumptions'!G17",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I17": {
          "formula": "H17*(1+$D$5)",
          "references": [
            "'Assumptions'!H17",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J17": {
          "formula": "I17*(1+$D$5)",
          "references": [
            "'Assumptions'!I17",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G18": {
          "formula": "F18*(1+$D$5)",
          "references": [
            "'Assumptions'!F18",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H18": {
          "formula": "G18*(1+$D$5)",
          "references": [
            "'Assumptions'!G18",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I18": {
          "formula": "H18*(1+$D$5)",
          "references": [
            "'Assumptions'!H18",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J18": {
          "formula": "I18*(1+$D$5)",
          "references": [
            "'Assumptions'!I18",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G19": {
          "formula": "F19*(1+$D$5)",
          "references": [
            "'Assumptions'!F19",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H19": {
          "formula": "G19*(1+$D$5)",
          "references": [
            "'Assumptions'!G19",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I19": {
          "formula": "H19*(1+$D$5)",
          "references": [
            "'Assumptions'!H19",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J19": {
          "formula": "I19*(1+$D$5)",
          "references": [
            "'Assumptions'!I19",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G20": {
          "formula": "F20*(1+$D$5)",
          "references": [
            "'Assumptions'!F20",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H20": {
          "formula": "G20*(1+$D$5)",
          "references": [
            "'Assumptions'!G20",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I20": {
          "formula": "H20*(1+$D$5)",
          "references": [
            "'Assumptions'!H20",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J20": {
          "formula": "I20*(1+$D$5)",
          "references": [
            "'Assumptions'!I20",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G21": {
          "formula": "F21*(1+$D$5)",
          "references": [
            "'Assumptions'!F21",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H21": {
          "formula": "G21*(1+$D$5)",
          "references": [
            "'Assumptions'!G21",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I21": {
          "formula": "H21*(1+$D$5)",
          "references": [
            "'Assumptions'!H21",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J21": {
          "formula": "I21*(1+$D$5)",
          "references": [
            "'Assumptions'!I21",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G22": {
          "formula": "F22*(1+$D$5)",
          "references": [
            "'Assumptions'!F22",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H22": {
          "formula": "G22*(1+$D$5)",
          "references": [
            "'Assumptions'!G22",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I22": {
          "formula": "H22*(1+$D$5)",
          "references": [
            "'Assumptions'!H22",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J22": {
          "formula": "I22*(1+$D$5)",
          "references": [
            "'Assumptions'!I22",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G23": {
          "formula": "F23*(1+$D$5)",
          "references": [
            "'Assumptions'!F23",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H23": {
          "formula": "G23*(1+$D$5)",
          "references": [
            "'Assumptions'!G23",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I23": {
          "formula": "H23*(1+$D$5)",
          "references": [
            "'Assumptions'!H23",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J23": {
          "formula": "I23*(1+$D$5)",
          "references": [
            "'Assumptions'!I23",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G24": {
          "formula": "F24*(1+$D$5)",
          "references": [
            "'Assumptions'!F24",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H24": {
          "formula": "G24*(1+$D$5)",
          "references": [
            "'Assumptions'!G24",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I24": {
          "formula": "H24*(1+$D$5)",
          "references": [
            "'Assumptions'!H24",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J24": {
          "formula": "I24*(1+$D$5)",
          "references": [
            "'Assumptions'!I24",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G25": {
          "formula": "F25*(1+$D$5)",
          "references": [
            "'Assumptions'!F25",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H25": {
          "formula": "G25*(1+$D$5)",
          "references": [
            "'Assumptions'!G25",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I25": {
          "formula": "H25*(1+$D$5)",
          "references": [
            "'Assumptions'!H25",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J25": {
          "formula": "I25*(1+$D$5)",
          "references": [
            "'Assumptions'!I25",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G26": {
          "formula": "F26*(1+$D$5)",
          "references": [
            "'Assumptions'!F26",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H26": {
          "formula": "G26*(1+$D$5)",
          "references": [
            "'Assumptions'!G26",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I26": {
          "formula": "H26*(1+$D$5)",
          "references": [
            "'Assumptions'!H26",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J26": {
          "formula": "I26*(1+$D$5)",
          "references": [
            "'Assumptions'!I26",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G27": {
          "formula": "F27*(1+$D$5)",
          "references": [
            "'Assumptions'!F27",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H27": {
          "formula": "G27*(1+$D$5)",
          "references": [
            "'Assumptions'!G27",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I27": {
          "formula": "H27*(1+$D$5)",
          "references": [
            "'Assumptions'!H27",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J27": {
          "formula": "I27*(1+$D$5)",
          "references": [
            "'Assumptions'!I27",
            "'Assumptions'!$D$5"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "offer_volume_2026": {
      "shape_sha256": "cf72b4649c0bb51aae50239267446fd8bc335d1ab5dea6b17a07a28927592206",
      "source_label": "Volume plan A1",
      "default_sources": {}
    },
    "offer_volume_2027": {
      "shape_sha256": "4d4499c81ff34740cd841215b70ccdb68166cc10a8812fac73c30fed0044fb8f",
      "source_label": "Volume plan A2",
      "default_sources": {}
    },
    "offer_volume_2028": {
      "shape_sha256": "69839fb6eebc18593413e5032ca918566a26e1e0012174d43b3d6de3be8de9bc",
      "source_label": "Volume plan A3",
      "default_sources": {}
    },
    "offer_volume_2029": {
      "shape_sha256": "3c7f8e18d205c02986ecee4dfbf19f6b89c2e591bf154b4c807957ce56094303",
      "source_label": "Volume plan A4",
      "default_sources": {}
    },
    "offer_volume_2030": {
      "shape_sha256": "be7e7c64c8080ab79fe911055d8d7e630ba908760cd28152f6cd2ad16931e928",
      "source_label": "Volume plan A5",
      "default_sources": {}
    },
    "offer_capacity_2026": {
      "shape_sha256": "d2afcd6fd7086b97ba0b5ab206a174c66888d838e0212d7bb57943eca6cd86fd",
      "source_label": "Capacité industrielle A1",
      "default_sources": {}
    },
    "offer_capacity_2027": {
      "shape_sha256": "7c8c4e294ceaffd911595c7d9919b76fa7c326fc52b0ab24cc40e18625d1cbc1",
      "source_label": "Capacité industrielle A2",
      "default_sources": {}
    },
    "offer_capacity_2028": {
      "shape_sha256": "d12abd6549174e58b60b99b9636bafcf78da63783bafd94dd58d02bb0a31c269",
      "source_label": "Capacité industrielle A3",
      "default_sources": {}
    },
    "offer_capacity_2029": {
      "shape_sha256": "cd48668c0e904167a5d9f136addf9fda6a5783c3c31e104feaf93f337de49767",
      "source_label": "Capacité industrielle A4",
      "default_sources": {}
    },
    "offer_capacity_2030": {
      "shape_sha256": "3c86c94c188464f989a88ab6c8fed6c385157ec6e03428dabc57c5c43ece8be4",
      "source_label": "Capacité industrielle A5",
      "default_sources": {}
    },
    "offer_payment_days": {
      "shape_sha256": "a1e39682c78dca61daf5173ef6baec2d942632389445e1a475e1cada5ce64a1d",
      "source_label": "Délai d’encaissement clients",
      "default_sources": {}
    },
    "offer_deposit_rate": {
      "shape_sha256": "814b0ec1ee643a58c98296d9fa265861012d75af7204844c7f4a16c100819481",
      "source_label": "Acompte",
      "default_sources": {}
    },
    "offer_deposit_lead": {
      "shape_sha256": "9724c158cde8dd8d2b97a860fa370000d35c9a0e37eb03ab63259c007b12b5ee",
      "source_label": "Acompte : anticipation",
      "default_sources": {}
    },
    "offer_milestone_rate": {
      "shape_sha256": "69d22b8f61aedf5cf29fe7f59fd69d1355bd44b1ce4a00ee608e71781731f551",
      "source_label": "Jalon",
      "default_sources": {}
    },
    "offer_milestone_lead": {
      "shape_sha256": "bfcf4194fb95a88d7914f6c83db7ab35211ff5714d464dffb0f17bf1fb60873b",
      "source_label": "Jalon : anticipation",
      "default_sources": {}
    },
    "offer_balance_rate": {
      "shape_sha256": "f0f4c087de7edb9ca9cdc79d058db8a561d4c658867fe0c9b0f6ce5cc52a127a",
      "source_label": "Solde",
      "default_sources": {}
    },
    "offer_status_source": {
      "shape_sha256": "4909dcdc9264b549ad6880a7037791644958fe2d60083b6f610b0d83b4052c12",
      "source_label": "Statut / qualité de l’hypothèse",
      "default_sources": {}
    },
    "offer_source": {
      "shape_sha256": "ca0425fb2e578d818332bafc4a33edd726a136064defaa45824605b9e13d0f28",
      "source_label": "Source commerciale",
      "default_sources": {}
    },
    "offer_price_2031": {
      "shape_sha256": "aada5be05bf2db001180b7f8a92b3bd693d4c0cc7141f031ae40b08503f038a0",
      "source_label": "price A6",
      "default_sources": {}
    },
    "offer_price_2032": {
      "shape_sha256": "b41870c7967ae3f45f3ef4e043605964ff4ac2544066329f2435faf91c74633b",
      "source_label": "price A7",
      "default_sources": {}
    },
    "offer_price_2033": {
      "shape_sha256": "3c8c09e2320dd13d5a0982a287ee0985ea530344da62eab49d1fb9147c082aab",
      "source_label": "price A8",
      "default_sources": {}
    },
    "offer_price_2034": {
      "shape_sha256": "47f842100691eb7ec604e8f711001d509d600806c64de4e80a1c02ebe762e637",
      "source_label": "price A9",
      "default_sources": {}
    },
    "offer_price_2035": {
      "shape_sha256": "db4d10ef13b2b4332e7df89668efe6f3edb79fb99add0173712ce2be733071fe",
      "source_label": "price A10",
      "default_sources": {}
    },
    "offer_volume_2031": {
      "shape_sha256": "68fd6cb621adc633a2ad9635cd68c2d185d1fc52193c9b401fb33f6e8c3257e6",
      "source_label": "volume A6",
      "default_sources": {}
    },
    "offer_volume_2032": {
      "shape_sha256": "c64597d02f883522bc452ebf536307e86c812dbe831eee1993797889649084d1",
      "source_label": "volume A7",
      "default_sources": {}
    },
    "offer_volume_2033": {
      "shape_sha256": "f45dbb5fca09f7d3dacfbfa926226f2dfb9578b91a084c1890aeed0e2bd371a9",
      "source_label": "volume A8",
      "default_sources": {}
    },
    "offer_volume_2034": {
      "shape_sha256": "0a15c82eec36e467b52c8f8ba298f5c0336fa32a78db316ad8851aec359ea0b3",
      "source_label": "volume A9",
      "default_sources": {}
    },
    "offer_volume_2035": {
      "shape_sha256": "6ad69abd1d37afc8f5dd1803b6e74820acdd90993f013010d812cf0c169c36a9",
      "source_label": "volume A10",
      "default_sources": {}
    },
    "offer_capacity_2031": {
      "shape_sha256": "a4da26ed20233d8f241a18b1975c60c287ba8038d2968ca4fc94a9ff2e7911b9",
      "source_label": "capacity A6",
      "default_sources": {}
    },
    "offer_capacity_2032": {
      "shape_sha256": "89ce0508df51547f3d1adf2d81aa539d80385362d080762f6ff1b2c4ae7debbc",
      "source_label": "capacity A7",
      "default_sources": {}
    },
    "offer_capacity_2033": {
      "shape_sha256": "b937773e55a73fd306b5a46367c6eaa399434b4380d0b334e68519589f7ab7d2",
      "source_label": "capacity A8",
      "default_sources": {}
    },
    "offer_capacity_2034": {
      "shape_sha256": "ec57ce382e42cf6dcc426e0f8cf73f76c5b21a8d7ef5ce1173747b9874010778",
      "source_label": "capacity A9",
      "default_sources": {}
    },
    "offer_capacity_2035": {
      "shape_sha256": "0294a5e203a7e157e674dbe8b5c14438f546d3e054902fdf3901e10096526ff1",
      "source_label": "capacity A10",
      "default_sources": {}
    },
    "contract_client": {
      "shape_sha256": "427969f1965af28d49f2e038d44f94626a10653a4437eacf663bc99badd4b511",
      "source_label": "Client / affaire",
      "default_sources": {}
    },
    "contract_offer": {
      "shape_sha256": "18db444a30955fae43e0e905edcf4af7e310fdbe0d0cfdb3ea6b16dde1bdef2d",
      "source_label": "Prestation",
      "default_sources": {}
    },
    "contract_quantity": {
      "shape_sha256": "854a3d9bde313fa4710ff32a804b7a54a4286d43965278941df53eac6022735a",
      "source_label": "Quantité",
      "default_sources": {}
    },
    "contract_unit_price": {
      "shape_sha256": "dfea63d9efe0dbd70251cd9b328ad46e7dc84e3883b302ff40581188490035c8",
      "source_label": "Prix négocié",
      "default_sources": {}
    },
    "contract_start": {
      "shape_sha256": "8445e5cd62a7e6dc0cc0132bfb0fde9e6c9d09ce5585669bc447b47244fdb412",
      "source_label": "Début du contrat",
      "default_sources": {}
    },
    "contract_end": {
      "shape_sha256": "e6ec1f28dd3176dd1d8d18a257295e61e550b76ef5c7a76bde80b7edbc42a11e",
      "source_label": "Fin du contrat",
      "default_sources": {}
    },
    "contract_recognition": {
      "shape_sha256": "5c5bc0f5200789645d78a343dc868b8e672c5e3600e4662cb28167155ba364bf",
      "source_label": "Mode de reconnaissance",
      "default_sources": {}
    },
    "contract_invoicing": {
      "shape_sha256": "99d4950a4ef2ff3f21b9ded7f78eada1cc8420c27f35a9f4616e20e22ab662b6",
      "source_label": "Mode de facturation",
      "default_sources": {}
    },
    "contract_deposit_rate": {
      "shape_sha256": "91222d14756e54d9dfda2e71fda44c3894b2eb5f252d8cd7511200027703fb34",
      "source_label": "Acompte",
      "default_sources": {}
    },
    "contract_deposit_date": {
      "shape_sha256": "07d01aae7d0a2c09bd08db139a53cc2f597067004a943a73947cca97d99ba890",
      "source_label": "Date de l’acompte",
      "default_sources": {}
    },
    "contract_milestone_rate": {
      "shape_sha256": "08a9b1bb6977349613eb8a5c16ed7f0071675751f82ddd53fd2c0921cc3f8f67",
      "source_label": "Jalon",
      "default_sources": {}
    },
    "contract_milestone_date": {
      "shape_sha256": "246ae616e55224a2dfab90e68d55904548146296da41cf5f01b973d8195c836c",
      "source_label": "Date du jalon",
      "default_sources": {}
    },
    "contract_balance_date": {
      "shape_sha256": "4f7f8b50d9c66f3255ba545a56331a4be522cac85f196abad66315ffce5cc2bc",
      "source_label": "Date du solde",
      "default_sources": {}
    },
    "contract_status": {
      "shape_sha256": "02dbb0b9cf6e7c26631fa8e99f05958b4ad457c8c8c9b2ffbfda7f223a201567",
      "source_label": "Statut",
      "default_sources": {}
    },
    "contract_weight": {
      "shape_sha256": "be4dd07a7071d95f3a691d40971745c74af9c80c22c7a880c1ded211d2740998",
      "source_label": "Pondération",
      "default_sources": {}
    },
    "contract_vat_regime": {
      "shape_sha256": "1f2f59c4e040625a460cab6777eff33f447e827a16a62f8fbc28e44625ab5541",
      "source_label": "Régime TVA dérogatoire du contrat",
      "default_sources": {}
    },
    "contract_vat_rate": {
      "shape_sha256": "76d5e8d79a3220a31dd5f472a5c4965401c8092d3b28244ffbfac03465b3bb69",
      "source_label": "Taux TVA dérogatoire du contrat",
      "default_sources": {}
    },
    "cogs_mode": {
      "shape_sha256": "87a1372dd376327b60c616a0cbe5ba8765774c83c8569fdf3dca4c10075182b8",
      "source_label": "Mode COGS",
      "default_sources": {}
    },
    "cogs_material": {
      "shape_sha256": "58a41dfcf1a2a06899a987e4c8f56b10a57da5d4121c9e1696f503444cb2fd49",
      "source_label": "Matière et achats",
      "default_sources": {}
    },
    "cogs_integration": {
      "shape_sha256": "876badf35ad204f274c8ea7144649ea6d71880e1611bb4c1c38390acbb68c55f",
      "source_label": "Intégration interne",
      "default_sources": {}
    },
    "cogs_testing": {
      "shape_sha256": "44cc85caa538b746d2e20ab123c5d0effe345ee413f8f4b5299ea4582e534c30",
      "source_label": "Essais et qualification",
      "default_sources": {}
    },
    "cogs_other": {
      "shape_sha256": "14a1b7dd61dc114a8a726977a602917a82942d71269d4a784648f7b667065667",
      "source_label": "Autres coûts directs",
      "default_sources": {}
    },
    "cogs_manual": {
      "shape_sha256": "d766f8ca24069640e804f65cc9633e86b17af3a865c4666cec6c357702ad28f9",
      "source_label": "COGS manuel",
      "default_sources": {}
    },
    "cogs_logistics": {
      "shape_sha256": "37f3fcf4e8f9368d6021d2c8734250d436fafac83e49b8b2a887239628e9ba83",
      "source_label": "Logistique et sous-traitance",
      "default_sources": {}
    },
    "cogs_warranty": {
      "shape_sha256": "4bcd3f76353c49eb15aad784de96260974a47509466db0773ebe2e7dd8dde093",
      "source_label": "Garantie et retours",
      "default_sources": {}
    },
    "cogs_margin_2026": {
      "shape_sha256": "838585fb9356eea5112f69f1a677358c2764345b1f17fb6da875c1a6f7ecc3e0",
      "source_label": "Marge cible A1",
      "default_sources": {}
    },
    "cogs_margin_2027": {
      "shape_sha256": "b3c7126c81e12878a2a0bc2ffebf70602c52d3cb5f1b869dd5614edd19f31c77",
      "source_label": "Marge cible A2",
      "default_sources": {}
    },
    "cogs_margin_2028": {
      "shape_sha256": "8af9a077724d04003fe98e50bd7b00cd19b8e49ed8075030181c1022f42de75b",
      "source_label": "Marge cible A3",
      "default_sources": {}
    },
    "cogs_margin_2029": {
      "shape_sha256": "6c9146bc67d0eccac327dee5282298171a98b9c1b7b43e78ebe009f0e97a89c5",
      "source_label": "Marge cible A4",
      "default_sources": {}
    },
    "cogs_margin_2030": {
      "shape_sha256": "edff3778861b7a5373e5f950b501faae9cac202ef176f18ebd50d69b62d2ded8",
      "source_label": "Marge cible A5",
      "default_sources": {}
    },
    "cogs_margin_2031": {
      "shape_sha256": "e5f0f40fa508311a57e48d1efd64694bd0dcf096d71aa785a8d60594253a63b2",
      "source_label": "Marge cible A6",
      "default_sources": {}
    },
    "cogs_margin_2032": {
      "shape_sha256": "2253c30f5d59a741f10d61715006617635cba5130e498a18d982b2f5df93b005",
      "source_label": "Marge cible A7",
      "default_sources": {}
    },
    "cogs_margin_2033": {
      "shape_sha256": "aa055f05c10e46ab589094a67246c27ac5f73c62998b2784ada9f5785e671f19",
      "source_label": "Marge cible A8",
      "default_sources": {}
    },
    "cogs_margin_2034": {
      "shape_sha256": "c5f3a8c661798cc979cbbbfd46d004ba15d69f1cd55d50535987d3c008209b0e",
      "source_label": "Marge cible A9",
      "default_sources": {}
    },
    "cogs_margin_2035": {
      "shape_sha256": "1cb7605d6a71785b63a16bd4a1a9c50eeea485b7bbff4b7dbb3a29d6930adc96",
      "source_label": "Marge cible A10",
      "default_sources": {}
    },
    "cogs_source": {
      "shape_sha256": "c64e3333b845f99ed949bb56bbe2400bcad02e0194e940dd95a3aae98f3dcbc3",
      "source_label": "Statut / source du coût",
      "default_sources": {}
    },
    "external_fixed": {
      "shape_sha256": "d3f5270768842009d45ae8be63273939b42e7716b788d4b30d932294e4b5629a",
      "source_label": "Base annuelle fixe",
      "default_sources": {}
    },
    "external_per_fte": {
      "shape_sha256": "1ec1e690a653f14816d8bba141eee2ae009f37eab3e7ae2d285d60e0fd6441e0",
      "source_label": "Coût par ETP",
      "default_sources": {}
    },
    "external_per_unit": {
      "shape_sha256": "74acf2776184440c6001259fc9bd9ce7eccaa869511ee71fb33930365f026bfa",
      "source_label": "Coût par unité",
      "default_sources": {}
    },
    "external_revenue_share": {
      "shape_sha256": "d3dcddb0bd72990b28ae57e074fa386f5ec875c30088b67e714c52f5880cc31f",
      "source_label": "Coût en part du CA",
      "default_sources": {}
    },
    "external_revenue_base": {
      "shape_sha256": "7da163dede3702fed3cae214f4e7d3f7e12557274a1d33d86c13cef4e1578819",
      "source_label": "Assiette du CA",
      "default_sources": {}
    },
    "external_fixed_assets_share": {
      "shape_sha256": "2c4a4c14d3adf483a0c7a9001f8a89cfd1d3423538cd555a52fd23a0f8b007be",
      "source_label": "Coût en part des immobilisations brutes",
      "default_sources": {}
    },
    "external_stock_share": {
      "shape_sha256": "2ec67a0c6c1538d06f3f34f0817ecd636cb76b4808bfcd183e568cf3187c9a67",
      "source_label": "Coût en part des stocks",
      "default_sources": {}
    },
    "external_local_inflation": {
      "shape_sha256": "bc45d0e1c033bc30cc34fc19b5e0bdd2cb6e60c87953e1b5ccc4535aacffbe00",
      "source_label": "Inflation propre à la nature de charges",
      "default_sources": {}
    },
    "employee_position": {
      "shape_sha256": "966379e0c2b707cc6c398bfa5ad940b7a341b9bdddc2daa56ba645e430a0bb21",
      "source_label": "Poste",
      "default_sources": {}
    },
    "employee_department": {
      "shape_sha256": "27e66e9cecbc16de40b6b0044292d872c6c9dd84d8cb1490b7dfca28737a22ff",
      "source_label": "Pôle",
      "default_sources": {}
    },
    "employee_analytic": {
      "shape_sha256": "e5ca019cb996920b92a1833b2ee0a591a76e841e13be09b899b7b4c87709b570",
      "source_label": "Affectation analytique",
      "default_sources": {}
    },
    "employee_rnd_share": {
      "shape_sha256": "7e61c4b463477ef1744f7c1a471dffaae78ed377f84e02c3f8bebc306be0b22a",
      "source_label": "Quote-part R&D",
      "default_sources": {}
    },
    "employee_start": {
      "shape_sha256": "364672f6ab965ac262bb56b8bc4fe039d881ce1593491533844c24f6baa58efc",
      "source_label": "Date d’entrée",
      "default_sources": {}
    },
    "employee_end": {
      "shape_sha256": "f88782be6b25023512598dc42afe9b9eb0ea84194d4170a46046707ab7ea3db7",
      "source_label": "Date de sortie",
      "default_sources": {}
    },
    "employee_fte": {
      "shape_sha256": "aee22839bbe4bf75e5472eafdcc8d9460bf564f94599df0a97c135c7f3e146c6",
      "source_label": "ETP",
      "default_sources": {}
    },
    "employee_salary": {
      "shape_sha256": "b271791d56e61c393edd03e1cb494eb1a7aff14bde3f928232f4867844b30c13",
      "source_label": "Salaire brut annuel base A1",
      "default_sources": {}
    },
    "employee_charges": {
      "shape_sha256": "1ba02280b72db6cb6662e9298b60a09b4b298246caee41347bcfda41c059fc04",
      "source_label": "Charges patronales propres au poste",
      "default_sources": {}
    },
    "employee_status": {
      "shape_sha256": "e3915bdde927a753d6247fd6b4914c28acf0c07af267045184ac4eafa43f4572",
      "source_label": "Statut du poste",
      "default_sources": {}
    },
    "employee_comment": {
      "shape_sha256": "668f2cff4337612a248cb2469cf9b02f5d6648f9ea8188f4ed61f9a564b30b56",
      "source_label": "Commentaire",
      "default_sources": {}
    },
    "employer_rate_barometer": {
      "shape_sha256": "7d121a8bab2390fb45b409066878be39479f5d9dbdf903b9cb1ccedc354ec94a",
      "source_label": "Barème indicatif des charges patronales",
      "default_sources": {}
    },
    "stock_coverage": {
      "shape_sha256": "beabf18e2ed97f018ebd452c56366ec76203c657fc15c17b5177e4ee1a79706e",
      "source_label": "Couverture de stock",
      "default_sources": {}
    },
    "supplier_payment_delay": {
      "shape_sha256": "1a90e286a2601e7f3400a06c753ec6ba4fa92b13add09081dc8c44e11bc77bbb",
      "source_label": "Délai de paiement fournisseurs",
      "default_sources": {}
    },
    "conventional_month_days": {
      "shape_sha256": "be6fba314500b67b85b88d4c09e6192699e5bcd03c028fe914a1be17e03fef46",
      "source_label": "Jours conventionnels par mois",
      "default_sources": {}
    },
    "industrial_capacity_factor": {
      "shape_sha256": "d5151d836a48490e767e7aaf244c537c5bc518ed6ed92fe923bfef7221290587",
      "source_label": "Flexeur de capacité industrielle",
      "default_sources": {}
    },
    "opening_receivables": {
      "shape_sha256": "643c2f818ecc20f24d90d28c47b391982da18f220f7ba88a58423b820eb306d2",
      "source_label": "Créances clients d’ouverture",
      "default_sources": {}
    },
    "opening_customer_advances": {
      "shape_sha256": "57500009766218f3ba99fde526e812ec2ac0e88dad59e775df8909c91774a0fd",
      "source_label": "Acomptes clients/PCA d’ouverture",
      "default_sources": {}
    },
    "opening_unbilled_revenue": {
      "shape_sha256": "d6dc5fec1612126b035490977fc2a1766e84cb87018cef6ac4855ec0a2f4dc54",
      "source_label": "Produits à recevoir/FAE d’ouverture",
      "default_sources": {}
    },
    "opening_stock": {
      "shape_sha256": "e2ec413e866aed0dfdde812726c29de8d110e2d2f7b3eb0f893b790b958b8d37",
      "source_label": "Stock d’ouverture",
      "default_sources": {}
    },
    "opening_payables": {
      "shape_sha256": "a82dafa5c35d4e974879b43508ed908219d36c21aa8119879a876c4f64e27793",
      "source_label": "Fournisseurs d’ouverture",
      "default_sources": {}
    },
    "installed_interceptors": {
      "shape_sha256": "f08749bd66f944d979662a384f3bbfe12d18fc1cf605fd10b82e04dff3653075",
      "source_label": "unités installées installés à l’ouverture",
      "default_sources": {}
    },
    "installed_oem": {
      "shape_sha256": "383d9cf163bb2774d5f8d55faafe5c56c9559d24bf9dfaa6b1d53b64063323f9",
      "source_label": "Modules OEM installés à l’ouverture",
      "default_sources": {}
    },
    "opening_receivables_cash_date": {
      "shape_sha256": "d5407f91b5bfe3da4cf8d507a3e754a98632c659dd10979fc652c69f0a57ca0b",
      "source_label": "Date d’encaissement des créances d’ouverture",
      "default_sources": {}
    },
    "opening_payables_cash_date": {
      "shape_sha256": "1947e309074c68f7355114b37d9f1146bee633c189b6d6f2eacca64a0148daaf",
      "source_label": "Date de règlement fournisseurs d’ouverture",
      "default_sources": {}
    },
    "active_horizon_years": {
      "shape_sha256": "6cb287efd9e9fbbfb41a7a6a2f4d100237971bd8018512e22c5b43ac788431f5",
      "source_label": "Nombre d’années actives",
      "default_sources": {}
    },
    "active_scenario": {
      "shape_sha256": "02aa8b57758654168402322296a57814dc9843dba399bfaf6cf995105d6eef86",
      "source_label": "Scénario actif",
      "default_sources": {}
    },
    "manual_shock_volume": {
      "shape_sha256": "6bf49638472c4d050af2844a8cce53704f24dcf4e7f9c097a1952b3aa43e0a5e",
      "source_label": "Choc manuel volume",
      "default_sources": {}
    },
    "manual_shock_price": {
      "shape_sha256": "9e2c7be7f30d98915f36e0dff6ea1c0a46cb9a5265353e4a8f48a30c950af579",
      "source_label": "Choc manuel price",
      "default_sources": {}
    },
    "manual_shock_direct_costs": {
      "shape_sha256": "12f4d774fe19f89701d7a0501d94776f3c3100c1e95b7b28f4c3af5ec355589c",
      "source_label": "Choc manuel direct_costs",
      "default_sources": {}
    },
    "manual_shock_external_costs": {
      "shape_sha256": "583c8cb52302a96d024b3306f52ccf8d31079ac21c921db72bf97bfc38bab20e",
      "source_label": "Choc manuel external_costs",
      "default_sources": {}
    },
    "manual_shock_payroll": {
      "shape_sha256": "d99893eb1bf0ff6574daa57cc145025cc4733846074fb767d0bbcd56e47a9dde",
      "source_label": "Choc manuel payroll",
      "default_sources": {}
    },
    "manual_shock_client_delay": {
      "shape_sha256": "1e761b553f192650cd7f93671eee3bd3d9dd2387afaff39e33a7c3b95d3e335d",
      "source_label": "Choc manuel client_delay",
      "default_sources": {}
    },
    "manual_shock_subsidies": {
      "shape_sha256": "b107e60b30434095969ec0ea6e5fa5b9468b4c0fe469b078f73edd8764d683cc",
      "source_label": "Choc manuel subsidies",
      "default_sources": {}
    },
    "manual_shock_capex": {
      "shape_sha256": "bbb6c5ab20711ad266c566ae61d88c46ddae12858f2bfd9016571b0aacdc1526",
      "source_label": "Choc manuel capex",
      "default_sources": {}
    },
    "manual_financing_delay": {
      "shape_sha256": "b001fd3a8a2e0397e8da28ea45398599ed6bf8ea28f63de3bf65a5ad38f8b770",
      "source_label": "Retard de financement manuel",
      "default_sources": {}
    },
    "manual_equity_envelope": {
      "shape_sha256": "b8b4d9bd61f7fa96fff020320e07e52da4a18cc9301aac96269831430c22c078",
      "source_label": "Enveloppe Equity manuelle",
      "default_sources": {}
    },
    "offer_volume_shock": {
      "shape_sha256": "b8ac2c075af34ad8c7a5fd8c19779826289a594637d26f1fc6af1c8bc75972ff",
      "source_label": "Choc de volume par offre / année A1–A10",
      "default_sources": {
        "D40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M40": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M41": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M42": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M43": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M44": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M45": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M46": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M47": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M48": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M49": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M50": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M51": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M52": {
          "formula": "$C$6",
          "references": [
            "'Sensi TCA'!$C$6"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "offer_price_shock": {
      "shape_sha256": "6a10ed3579ed9b441ab60ce394840b72436c3f19fdb20cfa666cbe3f114a003d",
      "source_label": "Choc de prix par offre / année A1–A10",
      "default_sources": {
        "D56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M56": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M57": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M58": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M59": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M60": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M61": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M62": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M63": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M64": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M65": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M66": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M67": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "D68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "E68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "G68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "I68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "L68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M68": {
          "formula": "$C$7",
          "references": [
            "'Sensi TCA'!$C$7"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "analysis_shock_volume": {
      "shape_sha256": "bafe575e8850174c54dc5db1d66866c48bdf0811ecc34070b7ba23e16071ede5",
      "source_label": "Choc d’analyse volume",
      "default_sources": {}
    },
    "analysis_shock_price": {
      "shape_sha256": "dab615a9ac3e53b56704696b6208bc8465c9b928617b35f0bc26336dd1e53c50",
      "source_label": "Choc d’analyse price",
      "default_sources": {}
    },
    "analysis_shock_direct_costs": {
      "shape_sha256": "1cf6dd6442fbf3b589fbfe232907f79fe717ea1b20b31e88aa9754d4bbe90bb3",
      "source_label": "Choc d’analyse direct_costs",
      "default_sources": {}
    },
    "analysis_shock_external_costs": {
      "shape_sha256": "c6f1d87dd7c7948fc445ffdf053f1b1eba387598b7c9bf48c5fad63c2d6f4591",
      "source_label": "Choc d’analyse external_costs",
      "default_sources": {}
    },
    "analysis_shock_payroll": {
      "shape_sha256": "bf2ccbaedd5e49df07cd96e3706f752e2e00872d4323e5ca2460dc3075c59428",
      "source_label": "Choc d’analyse payroll",
      "default_sources": {}
    },
    "analysis_shock_client_delay": {
      "shape_sha256": "38e3b85c1f40026cf65d8de3ee3a36b7e03ed272aea318199d566d8d34ebb876",
      "source_label": "Choc d’analyse client_delay",
      "default_sources": {}
    },
    "analysis_shock_subsidies": {
      "shape_sha256": "4f5872745500a887a3362a41e56c147606a1c40e3a2527c368ea642bbe05c8f7",
      "source_label": "Choc d’analyse subsidies",
      "default_sources": {}
    },
    "analysis_shock_capex": {
      "shape_sha256": "ad06b5e7cf59cb8bfd27f410055e5f6c71ce235f4a7236a354e055c60303aee9",
      "source_label": "Choc d’analyse capex",
      "default_sources": {}
    },
    "analysis_financing_delay": {
      "shape_sha256": "290ba8b81c26dd172efd005ecf128adb1454f79d8a5f0f33691ff6dc87620f3a",
      "source_label": "Retard de financement de l’analyse",
      "default_sources": {}
    },
    "runway_event_date": {
      "shape_sha256": "4275ebe29bb16a811a68610fd932a59daf781b374bd37c40c66e7d8dd6868699",
      "source_label": "Date de l’événement de liquidité étudié",
      "default_sources": {
        "E72": {
          "formula": "Valorisation!$D$15",
          "references": [
            "'Valorisation'!$D$15"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_b13_b72": {
      "shape_sha256": "5a2f84aeb899a2d7e13096937c6aea9d1cd5790f1cc9bfe222d5429138fdf7a7",
      "source_label": "Intitulé investissement",
      "default_sources": {}
    },
    "data_capex_c13_c72": {
      "shape_sha256": "c3e4f827c8aac56357d3c19fde58e2e3e8f11c68166f08cbb6653a47b48834e0",
      "source_label": "Typologie catalogue",
      "default_sources": {}
    },
    "data_capex_d13_d72": {
      "shape_sha256": "03989975d21e5fa154cb649b9b471209d9b12d4e590c92edb728949f1386d50e",
      "source_label": "Montant HT euros",
      "default_sources": {}
    },
    "data_capex_e13_e72": {
      "shape_sha256": "9352818d006e0c33968729465e4eb6954f310b47b2e1fd1ae05ebf809688d7b9",
      "source_label": "Date acquisition / début du bail",
      "default_sources": {}
    },
    "data_capex_g13_g72": {
      "shape_sha256": "485b61735e8cd8d1a028ac2fc1e056fb97ae1c0f3762cd3a1e5aaaf3638dc853",
      "source_label": "Affectation R&D",
      "default_sources": {}
    },
    "data_capex_i13_i72": {
      "shape_sha256": "9909c49607b0a757acbe65dc18d111411a37a49408a2f9af3584f862653f78e3",
      "source_label": "Mode de financement",
      "default_sources": {}
    },
    "data_capex_f13_f72": {
      "shape_sha256": "31f1db1c9c88ba610bc4074823a84387d47cfac4e0c582efd00e080b6d17ad8a",
      "source_label": "Durée amortissement en années",
      "default_sources": {
        "F13": {
          "formula": "IF($C13=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C13,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C13",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F14": {
          "formula": "IF($C14=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C14,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C14",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F15": {
          "formula": "IF($C15=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C15,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C15",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F16": {
          "formula": "IF($C16=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C16,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C16",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F17": {
          "formula": "IF($C17=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C17,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C17",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F18": {
          "formula": "IF($C18=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C18,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C18",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F19": {
          "formula": "IF($C19=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C19,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C19",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F20": {
          "formula": "IF($C20=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C20,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C20",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F21": {
          "formula": "IF($C21=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C21,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C21",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F22": {
          "formula": "IF($C22=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C22,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C22",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F23": {
          "formula": "IF($C23=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C23,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C23",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F24": {
          "formula": "IF($C24=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C24,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C24",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F25": {
          "formula": "IF($C25=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C25,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C25",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F26": {
          "formula": "IF($C26=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C26,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C26",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F27": {
          "formula": "IF($C27=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C27,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C27",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F28": {
          "formula": "IF($C28=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C28,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C28",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F29": {
          "formula": "IF($C29=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C29,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C29",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F30": {
          "formula": "IF($C30=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C30,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C30",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F31": {
          "formula": "IF($C31=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C31,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C31",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F32": {
          "formula": "IF($C32=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C32,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C32",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F33": {
          "formula": "IF($C33=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C33,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C33",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F34": {
          "formula": "IF($C34=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C34,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C34",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F35": {
          "formula": "IF($C35=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C35,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C35",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F36": {
          "formula": "IF($C36=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C36,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C36",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F37": {
          "formula": "IF($C37=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C37,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C37",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F38": {
          "formula": "IF($C38=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C38,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C38",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F39": {
          "formula": "IF($C39=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C39,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C39",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F40": {
          "formula": "IF($C40=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C40,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C40",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F41": {
          "formula": "IF($C41=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C41,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C41",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F42": {
          "formula": "IF($C42=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C42,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C42",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F43": {
          "formula": "IF($C43=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C43,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C43",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F44": {
          "formula": "IF($C44=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C44,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C44",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F45": {
          "formula": "IF($C45=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C45,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C45",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F46": {
          "formula": "IF($C46=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C46,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C46",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F47": {
          "formula": "IF($C47=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C47,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C47",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F48": {
          "formula": "IF($C48=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C48,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C48",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F49": {
          "formula": "IF($C49=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C49,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C49",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F50": {
          "formula": "IF($C50=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C50,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C50",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F51": {
          "formula": "IF($C51=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C51,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C51",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F52": {
          "formula": "IF($C52=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C52,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C52",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F53": {
          "formula": "IF($C53=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C53,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C53",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F54": {
          "formula": "IF($C54=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C54,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C54",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F55": {
          "formula": "IF($C55=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C55,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C55",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F56": {
          "formula": "IF($C56=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C56,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C56",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F57": {
          "formula": "IF($C57=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C57,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C57",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F58": {
          "formula": "IF($C58=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C58,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C58",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F59": {
          "formula": "IF($C59=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C59,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C59",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F60": {
          "formula": "IF($C60=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C60,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C60",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F61": {
          "formula": "IF($C61=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C61,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C61",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F62": {
          "formula": "IF($C62=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C62,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C62",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F63": {
          "formula": "IF($C63=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C63,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C63",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F64": {
          "formula": "IF($C64=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C64,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C64",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F65": {
          "formula": "IF($C65=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C65,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C65",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F66": {
          "formula": "IF($C66=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C66,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C66",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F67": {
          "formula": "IF($C67=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C67,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C67",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F68": {
          "formula": "IF($C68=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C68,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C68",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F69": {
          "formula": "IF($C69=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C69,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C69",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F70": {
          "formula": "IF($C70=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C70,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C70",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F71": {
          "formula": "IF($C71=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C71,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C71",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "F72": {
          "formula": "IF($C72=\"\",\"\",IFERROR(INDEX(Assumptions!$C$98:$C$121,MATCH($C72,Assumptions!$B$98:$B$121,0)),\"\"))",
          "references": [
            "'DATA CAPEX'!$C72",
            "'Assumptions'!$C$98:$C$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_h13_h72": {
      "shape_sha256": "e9fbc6efe0c49665b46b135d7a5f6c4531995b54f3bb50f1f27da1073a5fd30d",
      "source_label": "Part affectée R&D",
      "default_sources": {
        "H13": {
          "formula": "IF($C13=\"\",\"\",IF($G13=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C13,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C13",
            "'DATA CAPEX'!$G13",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H14": {
          "formula": "IF($C14=\"\",\"\",IF($G14=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C14,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C14",
            "'DATA CAPEX'!$G14",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H15": {
          "formula": "IF($C15=\"\",\"\",IF($G15=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C15,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C15",
            "'DATA CAPEX'!$G15",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H16": {
          "formula": "IF($C16=\"\",\"\",IF($G16=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C16,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C16",
            "'DATA CAPEX'!$G16",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H17": {
          "formula": "IF($C17=\"\",\"\",IF($G17=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C17,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C17",
            "'DATA CAPEX'!$G17",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H18": {
          "formula": "IF($C18=\"\",\"\",IF($G18=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C18,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C18",
            "'DATA CAPEX'!$G18",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H19": {
          "formula": "IF($C19=\"\",\"\",IF($G19=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C19,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C19",
            "'DATA CAPEX'!$G19",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H20": {
          "formula": "IF($C20=\"\",\"\",IF($G20=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C20,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C20",
            "'DATA CAPEX'!$G20",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H21": {
          "formula": "IF($C21=\"\",\"\",IF($G21=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C21,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C21",
            "'DATA CAPEX'!$G21",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H22": {
          "formula": "IF($C22=\"\",\"\",IF($G22=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C22,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C22",
            "'DATA CAPEX'!$G22",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H23": {
          "formula": "IF($C23=\"\",\"\",IF($G23=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C23,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C23",
            "'DATA CAPEX'!$G23",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H24": {
          "formula": "IF($C24=\"\",\"\",IF($G24=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C24,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C24",
            "'DATA CAPEX'!$G24",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H25": {
          "formula": "IF($C25=\"\",\"\",IF($G25=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C25,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C25",
            "'DATA CAPEX'!$G25",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H26": {
          "formula": "IF($C26=\"\",\"\",IF($G26=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C26,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C26",
            "'DATA CAPEX'!$G26",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H27": {
          "formula": "IF($C27=\"\",\"\",IF($G27=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C27,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C27",
            "'DATA CAPEX'!$G27",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H28": {
          "formula": "IF($C28=\"\",\"\",IF($G28=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C28,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C28",
            "'DATA CAPEX'!$G28",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H29": {
          "formula": "IF($C29=\"\",\"\",IF($G29=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C29,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C29",
            "'DATA CAPEX'!$G29",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H30": {
          "formula": "IF($C30=\"\",\"\",IF($G30=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C30,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C30",
            "'DATA CAPEX'!$G30",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H31": {
          "formula": "IF($C31=\"\",\"\",IF($G31=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C31,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C31",
            "'DATA CAPEX'!$G31",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H32": {
          "formula": "IF($C32=\"\",\"\",IF($G32=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C32,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C32",
            "'DATA CAPEX'!$G32",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H33": {
          "formula": "IF($C33=\"\",\"\",IF($G33=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C33,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C33",
            "'DATA CAPEX'!$G33",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H34": {
          "formula": "IF($C34=\"\",\"\",IF($G34=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C34,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C34",
            "'DATA CAPEX'!$G34",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H35": {
          "formula": "IF($C35=\"\",\"\",IF($G35=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C35,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C35",
            "'DATA CAPEX'!$G35",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H36": {
          "formula": "IF($C36=\"\",\"\",IF($G36=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C36,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C36",
            "'DATA CAPEX'!$G36",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H37": {
          "formula": "IF($C37=\"\",\"\",IF($G37=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C37,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C37",
            "'DATA CAPEX'!$G37",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H38": {
          "formula": "IF($C38=\"\",\"\",IF($G38=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C38,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C38",
            "'DATA CAPEX'!$G38",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H39": {
          "formula": "IF($C39=\"\",\"\",IF($G39=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C39,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C39",
            "'DATA CAPEX'!$G39",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H40": {
          "formula": "IF($C40=\"\",\"\",IF($G40=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C40,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C40",
            "'DATA CAPEX'!$G40",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H41": {
          "formula": "IF($C41=\"\",\"\",IF($G41=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C41,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C41",
            "'DATA CAPEX'!$G41",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H42": {
          "formula": "IF($C42=\"\",\"\",IF($G42=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C42,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C42",
            "'DATA CAPEX'!$G42",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H43": {
          "formula": "IF($C43=\"\",\"\",IF($G43=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C43,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C43",
            "'DATA CAPEX'!$G43",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H44": {
          "formula": "IF($C44=\"\",\"\",IF($G44=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C44,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C44",
            "'DATA CAPEX'!$G44",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H45": {
          "formula": "IF($C45=\"\",\"\",IF($G45=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C45,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C45",
            "'DATA CAPEX'!$G45",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H46": {
          "formula": "IF($C46=\"\",\"\",IF($G46=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C46,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C46",
            "'DATA CAPEX'!$G46",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H47": {
          "formula": "IF($C47=\"\",\"\",IF($G47=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C47,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C47",
            "'DATA CAPEX'!$G47",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H48": {
          "formula": "IF($C48=\"\",\"\",IF($G48=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C48,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C48",
            "'DATA CAPEX'!$G48",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H49": {
          "formula": "IF($C49=\"\",\"\",IF($G49=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C49,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C49",
            "'DATA CAPEX'!$G49",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H50": {
          "formula": "IF($C50=\"\",\"\",IF($G50=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C50,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C50",
            "'DATA CAPEX'!$G50",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H51": {
          "formula": "IF($C51=\"\",\"\",IF($G51=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C51,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C51",
            "'DATA CAPEX'!$G51",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H52": {
          "formula": "IF($C52=\"\",\"\",IF($G52=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C52,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C52",
            "'DATA CAPEX'!$G52",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H53": {
          "formula": "IF($C53=\"\",\"\",IF($G53=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C53,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C53",
            "'DATA CAPEX'!$G53",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H54": {
          "formula": "IF($C54=\"\",\"\",IF($G54=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C54,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C54",
            "'DATA CAPEX'!$G54",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H55": {
          "formula": "IF($C55=\"\",\"\",IF($G55=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C55,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C55",
            "'DATA CAPEX'!$G55",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H56": {
          "formula": "IF($C56=\"\",\"\",IF($G56=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C56,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C56",
            "'DATA CAPEX'!$G56",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H57": {
          "formula": "IF($C57=\"\",\"\",IF($G57=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C57,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C57",
            "'DATA CAPEX'!$G57",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H58": {
          "formula": "IF($C58=\"\",\"\",IF($G58=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C58,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C58",
            "'DATA CAPEX'!$G58",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H59": {
          "formula": "IF($C59=\"\",\"\",IF($G59=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C59,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C59",
            "'DATA CAPEX'!$G59",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H60": {
          "formula": "IF($C60=\"\",\"\",IF($G60=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C60,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C60",
            "'DATA CAPEX'!$G60",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H61": {
          "formula": "IF($C61=\"\",\"\",IF($G61=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C61,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C61",
            "'DATA CAPEX'!$G61",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H62": {
          "formula": "IF($C62=\"\",\"\",IF($G62=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C62,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C62",
            "'DATA CAPEX'!$G62",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H63": {
          "formula": "IF($C63=\"\",\"\",IF($G63=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C63,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C63",
            "'DATA CAPEX'!$G63",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H64": {
          "formula": "IF($C64=\"\",\"\",IF($G64=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C64,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C64",
            "'DATA CAPEX'!$G64",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H65": {
          "formula": "IF($C65=\"\",\"\",IF($G65=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C65,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C65",
            "'DATA CAPEX'!$G65",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H66": {
          "formula": "IF($C66=\"\",\"\",IF($G66=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C66,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C66",
            "'DATA CAPEX'!$G66",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H67": {
          "formula": "IF($C67=\"\",\"\",IF($G67=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C67,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C67",
            "'DATA CAPEX'!$G67",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H68": {
          "formula": "IF($C68=\"\",\"\",IF($G68=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C68,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C68",
            "'DATA CAPEX'!$G68",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H69": {
          "formula": "IF($C69=\"\",\"\",IF($G69=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C69,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C69",
            "'DATA CAPEX'!$G69",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H70": {
          "formula": "IF($C70=\"\",\"\",IF($G70=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C70,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C70",
            "'DATA CAPEX'!$G70",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H71": {
          "formula": "IF($C71=\"\",\"\",IF($G71=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C71,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C71",
            "'DATA CAPEX'!$G71",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "H72": {
          "formula": "IF($C72=\"\",\"\",IF($G72=\"Non\",0,IFERROR(INDEX(Assumptions!$D$98:$D$121,MATCH($C72,Assumptions!$B$98:$B$121,0)),0)))",
          "references": [
            "'DATA CAPEX'!$C72",
            "'DATA CAPEX'!$G72",
            "'Assumptions'!$D$98:$D$121",
            "'Assumptions'!$B$98:$B$121"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_j13_j72": {
      "shape_sha256": "174ee4aeca6f5f1e9ac2352d88d50d0ef6397d9a8c54a08865dea5b87e74cb9f",
      "source_label": "Durée crédit-bail en années",
      "default_sources": {
        "J13": {
          "formula": "IF($I13<>\"Crédit-bail\",\"\",IF(N($F13)=0,\"\",N($F13)))",
          "references": [
            "'DATA CAPEX'!$I13",
            "'DATA CAPEX'!$F13"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J14": {
          "formula": "IF($I14<>\"Crédit-bail\",\"\",IF(N($F14)=0,\"\",N($F14)))",
          "references": [
            "'DATA CAPEX'!$I14",
            "'DATA CAPEX'!$F14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J15": {
          "formula": "IF($I15<>\"Crédit-bail\",\"\",IF(N($F15)=0,\"\",N($F15)))",
          "references": [
            "'DATA CAPEX'!$I15",
            "'DATA CAPEX'!$F15"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J16": {
          "formula": "IF($I16<>\"Crédit-bail\",\"\",IF(N($F16)=0,\"\",N($F16)))",
          "references": [
            "'DATA CAPEX'!$I16",
            "'DATA CAPEX'!$F16"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J17": {
          "formula": "IF($I17<>\"Crédit-bail\",\"\",IF(N($F17)=0,\"\",N($F17)))",
          "references": [
            "'DATA CAPEX'!$I17",
            "'DATA CAPEX'!$F17"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J18": {
          "formula": "IF($I18<>\"Crédit-bail\",\"\",IF(N($F18)=0,\"\",N($F18)))",
          "references": [
            "'DATA CAPEX'!$I18",
            "'DATA CAPEX'!$F18"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J19": {
          "formula": "IF($I19<>\"Crédit-bail\",\"\",IF(N($F19)=0,\"\",N($F19)))",
          "references": [
            "'DATA CAPEX'!$I19",
            "'DATA CAPEX'!$F19"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J20": {
          "formula": "IF($I20<>\"Crédit-bail\",\"\",IF(N($F20)=0,\"\",N($F20)))",
          "references": [
            "'DATA CAPEX'!$I20",
            "'DATA CAPEX'!$F20"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J21": {
          "formula": "IF($I21<>\"Crédit-bail\",\"\",IF(N($F21)=0,\"\",N($F21)))",
          "references": [
            "'DATA CAPEX'!$I21",
            "'DATA CAPEX'!$F21"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J22": {
          "formula": "IF($I22<>\"Crédit-bail\",\"\",IF(N($F22)=0,\"\",N($F22)))",
          "references": [
            "'DATA CAPEX'!$I22",
            "'DATA CAPEX'!$F22"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J23": {
          "formula": "IF($I23<>\"Crédit-bail\",\"\",IF(N($F23)=0,\"\",N($F23)))",
          "references": [
            "'DATA CAPEX'!$I23",
            "'DATA CAPEX'!$F23"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J24": {
          "formula": "IF($I24<>\"Crédit-bail\",\"\",IF(N($F24)=0,\"\",N($F24)))",
          "references": [
            "'DATA CAPEX'!$I24",
            "'DATA CAPEX'!$F24"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J25": {
          "formula": "IF($I25<>\"Crédit-bail\",\"\",IF(N($F25)=0,\"\",N($F25)))",
          "references": [
            "'DATA CAPEX'!$I25",
            "'DATA CAPEX'!$F25"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J26": {
          "formula": "IF($I26<>\"Crédit-bail\",\"\",IF(N($F26)=0,\"\",N($F26)))",
          "references": [
            "'DATA CAPEX'!$I26",
            "'DATA CAPEX'!$F26"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J27": {
          "formula": "IF($I27<>\"Crédit-bail\",\"\",IF(N($F27)=0,\"\",N($F27)))",
          "references": [
            "'DATA CAPEX'!$I27",
            "'DATA CAPEX'!$F27"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J28": {
          "formula": "IF($I28<>\"Crédit-bail\",\"\",IF(N($F28)=0,\"\",N($F28)))",
          "references": [
            "'DATA CAPEX'!$I28",
            "'DATA CAPEX'!$F28"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J29": {
          "formula": "IF($I29<>\"Crédit-bail\",\"\",IF(N($F29)=0,\"\",N($F29)))",
          "references": [
            "'DATA CAPEX'!$I29",
            "'DATA CAPEX'!$F29"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J30": {
          "formula": "IF($I30<>\"Crédit-bail\",\"\",IF(N($F30)=0,\"\",N($F30)))",
          "references": [
            "'DATA CAPEX'!$I30",
            "'DATA CAPEX'!$F30"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J31": {
          "formula": "IF($I31<>\"Crédit-bail\",\"\",IF(N($F31)=0,\"\",N($F31)))",
          "references": [
            "'DATA CAPEX'!$I31",
            "'DATA CAPEX'!$F31"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J32": {
          "formula": "IF($I32<>\"Crédit-bail\",\"\",IF(N($F32)=0,\"\",N($F32)))",
          "references": [
            "'DATA CAPEX'!$I32",
            "'DATA CAPEX'!$F32"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J33": {
          "formula": "IF($I33<>\"Crédit-bail\",\"\",IF(N($F33)=0,\"\",N($F33)))",
          "references": [
            "'DATA CAPEX'!$I33",
            "'DATA CAPEX'!$F33"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J34": {
          "formula": "IF($I34<>\"Crédit-bail\",\"\",IF(N($F34)=0,\"\",N($F34)))",
          "references": [
            "'DATA CAPEX'!$I34",
            "'DATA CAPEX'!$F34"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J35": {
          "formula": "IF($I35<>\"Crédit-bail\",\"\",IF(N($F35)=0,\"\",N($F35)))",
          "references": [
            "'DATA CAPEX'!$I35",
            "'DATA CAPEX'!$F35"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J36": {
          "formula": "IF($I36<>\"Crédit-bail\",\"\",IF(N($F36)=0,\"\",N($F36)))",
          "references": [
            "'DATA CAPEX'!$I36",
            "'DATA CAPEX'!$F36"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J37": {
          "formula": "IF($I37<>\"Crédit-bail\",\"\",IF(N($F37)=0,\"\",N($F37)))",
          "references": [
            "'DATA CAPEX'!$I37",
            "'DATA CAPEX'!$F37"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J38": {
          "formula": "IF($I38<>\"Crédit-bail\",\"\",IF(N($F38)=0,\"\",N($F38)))",
          "references": [
            "'DATA CAPEX'!$I38",
            "'DATA CAPEX'!$F38"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J39": {
          "formula": "IF($I39<>\"Crédit-bail\",\"\",IF(N($F39)=0,\"\",N($F39)))",
          "references": [
            "'DATA CAPEX'!$I39",
            "'DATA CAPEX'!$F39"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J40": {
          "formula": "IF($I40<>\"Crédit-bail\",\"\",IF(N($F40)=0,\"\",N($F40)))",
          "references": [
            "'DATA CAPEX'!$I40",
            "'DATA CAPEX'!$F40"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J41": {
          "formula": "IF($I41<>\"Crédit-bail\",\"\",IF(N($F41)=0,\"\",N($F41)))",
          "references": [
            "'DATA CAPEX'!$I41",
            "'DATA CAPEX'!$F41"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J42": {
          "formula": "IF($I42<>\"Crédit-bail\",\"\",IF(N($F42)=0,\"\",N($F42)))",
          "references": [
            "'DATA CAPEX'!$I42",
            "'DATA CAPEX'!$F42"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J43": {
          "formula": "IF($I43<>\"Crédit-bail\",\"\",IF(N($F43)=0,\"\",N($F43)))",
          "references": [
            "'DATA CAPEX'!$I43",
            "'DATA CAPEX'!$F43"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J44": {
          "formula": "IF($I44<>\"Crédit-bail\",\"\",IF(N($F44)=0,\"\",N($F44)))",
          "references": [
            "'DATA CAPEX'!$I44",
            "'DATA CAPEX'!$F44"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J45": {
          "formula": "IF($I45<>\"Crédit-bail\",\"\",IF(N($F45)=0,\"\",N($F45)))",
          "references": [
            "'DATA CAPEX'!$I45",
            "'DATA CAPEX'!$F45"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J46": {
          "formula": "IF($I46<>\"Crédit-bail\",\"\",IF(N($F46)=0,\"\",N($F46)))",
          "references": [
            "'DATA CAPEX'!$I46",
            "'DATA CAPEX'!$F46"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J47": {
          "formula": "IF($I47<>\"Crédit-bail\",\"\",IF(N($F47)=0,\"\",N($F47)))",
          "references": [
            "'DATA CAPEX'!$I47",
            "'DATA CAPEX'!$F47"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J48": {
          "formula": "IF($I48<>\"Crédit-bail\",\"\",IF(N($F48)=0,\"\",N($F48)))",
          "references": [
            "'DATA CAPEX'!$I48",
            "'DATA CAPEX'!$F48"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J49": {
          "formula": "IF($I49<>\"Crédit-bail\",\"\",IF(N($F49)=0,\"\",N($F49)))",
          "references": [
            "'DATA CAPEX'!$I49",
            "'DATA CAPEX'!$F49"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J50": {
          "formula": "IF($I50<>\"Crédit-bail\",\"\",IF(N($F50)=0,\"\",N($F50)))",
          "references": [
            "'DATA CAPEX'!$I50",
            "'DATA CAPEX'!$F50"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J51": {
          "formula": "IF($I51<>\"Crédit-bail\",\"\",IF(N($F51)=0,\"\",N($F51)))",
          "references": [
            "'DATA CAPEX'!$I51",
            "'DATA CAPEX'!$F51"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J52": {
          "formula": "IF($I52<>\"Crédit-bail\",\"\",IF(N($F52)=0,\"\",N($F52)))",
          "references": [
            "'DATA CAPEX'!$I52",
            "'DATA CAPEX'!$F52"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J53": {
          "formula": "IF($I53<>\"Crédit-bail\",\"\",IF(N($F53)=0,\"\",N($F53)))",
          "references": [
            "'DATA CAPEX'!$I53",
            "'DATA CAPEX'!$F53"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J54": {
          "formula": "IF($I54<>\"Crédit-bail\",\"\",IF(N($F54)=0,\"\",N($F54)))",
          "references": [
            "'DATA CAPEX'!$I54",
            "'DATA CAPEX'!$F54"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J55": {
          "formula": "IF($I55<>\"Crédit-bail\",\"\",IF(N($F55)=0,\"\",N($F55)))",
          "references": [
            "'DATA CAPEX'!$I55",
            "'DATA CAPEX'!$F55"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J56": {
          "formula": "IF($I56<>\"Crédit-bail\",\"\",IF(N($F56)=0,\"\",N($F56)))",
          "references": [
            "'DATA CAPEX'!$I56",
            "'DATA CAPEX'!$F56"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J57": {
          "formula": "IF($I57<>\"Crédit-bail\",\"\",IF(N($F57)=0,\"\",N($F57)))",
          "references": [
            "'DATA CAPEX'!$I57",
            "'DATA CAPEX'!$F57"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J58": {
          "formula": "IF($I58<>\"Crédit-bail\",\"\",IF(N($F58)=0,\"\",N($F58)))",
          "references": [
            "'DATA CAPEX'!$I58",
            "'DATA CAPEX'!$F58"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J59": {
          "formula": "IF($I59<>\"Crédit-bail\",\"\",IF(N($F59)=0,\"\",N($F59)))",
          "references": [
            "'DATA CAPEX'!$I59",
            "'DATA CAPEX'!$F59"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J60": {
          "formula": "IF($I60<>\"Crédit-bail\",\"\",IF(N($F60)=0,\"\",N($F60)))",
          "references": [
            "'DATA CAPEX'!$I60",
            "'DATA CAPEX'!$F60"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J61": {
          "formula": "IF($I61<>\"Crédit-bail\",\"\",IF(N($F61)=0,\"\",N($F61)))",
          "references": [
            "'DATA CAPEX'!$I61",
            "'DATA CAPEX'!$F61"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J62": {
          "formula": "IF($I62<>\"Crédit-bail\",\"\",IF(N($F62)=0,\"\",N($F62)))",
          "references": [
            "'DATA CAPEX'!$I62",
            "'DATA CAPEX'!$F62"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J63": {
          "formula": "IF($I63<>\"Crédit-bail\",\"\",IF(N($F63)=0,\"\",N($F63)))",
          "references": [
            "'DATA CAPEX'!$I63",
            "'DATA CAPEX'!$F63"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J64": {
          "formula": "IF($I64<>\"Crédit-bail\",\"\",IF(N($F64)=0,\"\",N($F64)))",
          "references": [
            "'DATA CAPEX'!$I64",
            "'DATA CAPEX'!$F64"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J65": {
          "formula": "IF($I65<>\"Crédit-bail\",\"\",IF(N($F65)=0,\"\",N($F65)))",
          "references": [
            "'DATA CAPEX'!$I65",
            "'DATA CAPEX'!$F65"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J66": {
          "formula": "IF($I66<>\"Crédit-bail\",\"\",IF(N($F66)=0,\"\",N($F66)))",
          "references": [
            "'DATA CAPEX'!$I66",
            "'DATA CAPEX'!$F66"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J67": {
          "formula": "IF($I67<>\"Crédit-bail\",\"\",IF(N($F67)=0,\"\",N($F67)))",
          "references": [
            "'DATA CAPEX'!$I67",
            "'DATA CAPEX'!$F67"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J68": {
          "formula": "IF($I68<>\"Crédit-bail\",\"\",IF(N($F68)=0,\"\",N($F68)))",
          "references": [
            "'DATA CAPEX'!$I68",
            "'DATA CAPEX'!$F68"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J69": {
          "formula": "IF($I69<>\"Crédit-bail\",\"\",IF(N($F69)=0,\"\",N($F69)))",
          "references": [
            "'DATA CAPEX'!$I69",
            "'DATA CAPEX'!$F69"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J70": {
          "formula": "IF($I70<>\"Crédit-bail\",\"\",IF(N($F70)=0,\"\",N($F70)))",
          "references": [
            "'DATA CAPEX'!$I70",
            "'DATA CAPEX'!$F70"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J71": {
          "formula": "IF($I71<>\"Crédit-bail\",\"\",IF(N($F71)=0,\"\",N($F71)))",
          "references": [
            "'DATA CAPEX'!$I71",
            "'DATA CAPEX'!$F71"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J72": {
          "formula": "IF($I72<>\"Crédit-bail\",\"\",IF(N($F72)=0,\"\",N($F72)))",
          "references": [
            "'DATA CAPEX'!$I72",
            "'DATA CAPEX'!$F72"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_k13_k72": {
      "shape_sha256": "eeed9dd5a0a4cd1d7f29631ec285cc0d687555406a5357c6a6013bcc9fa9b33a",
      "source_label": "Taux annuel crédit-bail",
      "default_sources": {
        "K13": {
          "formula": "IF($I13<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I13",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K14": {
          "formula": "IF($I14<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I14",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K15": {
          "formula": "IF($I15<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I15",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K16": {
          "formula": "IF($I16<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I16",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K17": {
          "formula": "IF($I17<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I17",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K18": {
          "formula": "IF($I18<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I18",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K19": {
          "formula": "IF($I19<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I19",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K20": {
          "formula": "IF($I20<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I20",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K21": {
          "formula": "IF($I21<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I21",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K22": {
          "formula": "IF($I22<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I22",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K23": {
          "formula": "IF($I23<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I23",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K24": {
          "formula": "IF($I24<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I24",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K25": {
          "formula": "IF($I25<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I25",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K26": {
          "formula": "IF($I26<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I26",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K27": {
          "formula": "IF($I27<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I27",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K28": {
          "formula": "IF($I28<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I28",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K29": {
          "formula": "IF($I29<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I29",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K30": {
          "formula": "IF($I30<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I30",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K31": {
          "formula": "IF($I31<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I31",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K32": {
          "formula": "IF($I32<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I32",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K33": {
          "formula": "IF($I33<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I33",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K34": {
          "formula": "IF($I34<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I34",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K35": {
          "formula": "IF($I35<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I35",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K36": {
          "formula": "IF($I36<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I36",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K37": {
          "formula": "IF($I37<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I37",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K38": {
          "formula": "IF($I38<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I38",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K39": {
          "formula": "IF($I39<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I39",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K40": {
          "formula": "IF($I40<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I40",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K41": {
          "formula": "IF($I41<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I41",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K42": {
          "formula": "IF($I42<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I42",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K43": {
          "formula": "IF($I43<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I43",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K44": {
          "formula": "IF($I44<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I44",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K45": {
          "formula": "IF($I45<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I45",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K46": {
          "formula": "IF($I46<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I46",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K47": {
          "formula": "IF($I47<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I47",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K48": {
          "formula": "IF($I48<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I48",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K49": {
          "formula": "IF($I49<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I49",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K50": {
          "formula": "IF($I50<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I50",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K51": {
          "formula": "IF($I51<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I51",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K52": {
          "formula": "IF($I52<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I52",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K53": {
          "formula": "IF($I53<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I53",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K54": {
          "formula": "IF($I54<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I54",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K55": {
          "formula": "IF($I55<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I55",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K56": {
          "formula": "IF($I56<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I56",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K57": {
          "formula": "IF($I57<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I57",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K58": {
          "formula": "IF($I58<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I58",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K59": {
          "formula": "IF($I59<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I59",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K60": {
          "formula": "IF($I60<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I60",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K61": {
          "formula": "IF($I61<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I61",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K62": {
          "formula": "IF($I62<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I62",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K63": {
          "formula": "IF($I63<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I63",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K64": {
          "formula": "IF($I64<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I64",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K65": {
          "formula": "IF($I65<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I65",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K66": {
          "formula": "IF($I66<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I66",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K67": {
          "formula": "IF($I67<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I67",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K68": {
          "formula": "IF($I68<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I68",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K69": {
          "formula": "IF($I69<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I69",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K70": {
          "formula": "IF($I70<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I70",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K71": {
          "formula": "IF($I71<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I71",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "K72": {
          "formula": "IF($I72<>\"Crédit-bail\",\"\",Assumptions!$D$91)",
          "references": [
            "'DATA CAPEX'!$I72",
            "'Assumptions'!$D$91"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_m13_m72": {
      "shape_sha256": "87c36c120c0616793752beda107b2d8fa9334c6e4f7c1479a7e6abb6e3986d8c",
      "source_label": "Nature de l’immobilisation",
      "default_sources": {
        "M13": {
          "formula": "IF($B13=\"\",\"\",IF(OR($C13=\"Logiciels de conception et simulation\",$C13=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B13",
            "'DATA CAPEX'!$C13"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M14": {
          "formula": "IF($B14=\"\",\"\",IF(OR($C14=\"Logiciels de conception et simulation\",$C14=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B14",
            "'DATA CAPEX'!$C14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M15": {
          "formula": "IF($B15=\"\",\"\",IF(OR($C15=\"Logiciels de conception et simulation\",$C15=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B15",
            "'DATA CAPEX'!$C15"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M16": {
          "formula": "IF($B16=\"\",\"\",IF(OR($C16=\"Logiciels de conception et simulation\",$C16=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B16",
            "'DATA CAPEX'!$C16"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M17": {
          "formula": "IF($B17=\"\",\"\",IF(OR($C17=\"Logiciels de conception et simulation\",$C17=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B17",
            "'DATA CAPEX'!$C17"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M18": {
          "formula": "IF($B18=\"\",\"\",IF(OR($C18=\"Logiciels de conception et simulation\",$C18=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B18",
            "'DATA CAPEX'!$C18"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M19": {
          "formula": "IF($B19=\"\",\"\",IF(OR($C19=\"Logiciels de conception et simulation\",$C19=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B19",
            "'DATA CAPEX'!$C19"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M20": {
          "formula": "IF($B20=\"\",\"\",IF(OR($C20=\"Logiciels de conception et simulation\",$C20=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B20",
            "'DATA CAPEX'!$C20"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M21": {
          "formula": "IF($B21=\"\",\"\",IF(OR($C21=\"Logiciels de conception et simulation\",$C21=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B21",
            "'DATA CAPEX'!$C21"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M22": {
          "formula": "IF($B22=\"\",\"\",IF(OR($C22=\"Logiciels de conception et simulation\",$C22=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B22",
            "'DATA CAPEX'!$C22"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M23": {
          "formula": "IF($B23=\"\",\"\",IF(OR($C23=\"Logiciels de conception et simulation\",$C23=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B23",
            "'DATA CAPEX'!$C23"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M24": {
          "formula": "IF($B24=\"\",\"\",IF(OR($C24=\"Logiciels de conception et simulation\",$C24=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B24",
            "'DATA CAPEX'!$C24"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M25": {
          "formula": "IF($B25=\"\",\"\",IF(OR($C25=\"Logiciels de conception et simulation\",$C25=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B25",
            "'DATA CAPEX'!$C25"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M26": {
          "formula": "IF($B26=\"\",\"\",IF(OR($C26=\"Logiciels de conception et simulation\",$C26=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B26",
            "'DATA CAPEX'!$C26"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M27": {
          "formula": "IF($B27=\"\",\"\",IF(OR($C27=\"Logiciels de conception et simulation\",$C27=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B27",
            "'DATA CAPEX'!$C27"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M28": {
          "formula": "IF($B28=\"\",\"\",IF(OR($C28=\"Logiciels de conception et simulation\",$C28=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B28",
            "'DATA CAPEX'!$C28"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M29": {
          "formula": "IF($B29=\"\",\"\",IF(OR($C29=\"Logiciels de conception et simulation\",$C29=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B29",
            "'DATA CAPEX'!$C29"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M30": {
          "formula": "IF($B30=\"\",\"\",IF(OR($C30=\"Logiciels de conception et simulation\",$C30=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B30",
            "'DATA CAPEX'!$C30"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M31": {
          "formula": "IF($B31=\"\",\"\",IF(OR($C31=\"Logiciels de conception et simulation\",$C31=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B31",
            "'DATA CAPEX'!$C31"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M32": {
          "formula": "IF($B32=\"\",\"\",IF(OR($C32=\"Logiciels de conception et simulation\",$C32=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B32",
            "'DATA CAPEX'!$C32"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M33": {
          "formula": "IF($B33=\"\",\"\",IF(OR($C33=\"Logiciels de conception et simulation\",$C33=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B33",
            "'DATA CAPEX'!$C33"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M34": {
          "formula": "IF($B34=\"\",\"\",IF(OR($C34=\"Logiciels de conception et simulation\",$C34=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B34",
            "'DATA CAPEX'!$C34"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M35": {
          "formula": "IF($B35=\"\",\"\",IF(OR($C35=\"Logiciels de conception et simulation\",$C35=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B35",
            "'DATA CAPEX'!$C35"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M36": {
          "formula": "IF($B36=\"\",\"\",IF(OR($C36=\"Logiciels de conception et simulation\",$C36=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B36",
            "'DATA CAPEX'!$C36"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M37": {
          "formula": "IF($B37=\"\",\"\",IF(OR($C37=\"Logiciels de conception et simulation\",$C37=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B37",
            "'DATA CAPEX'!$C37"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M38": {
          "formula": "IF($B38=\"\",\"\",IF(OR($C38=\"Logiciels de conception et simulation\",$C38=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B38",
            "'DATA CAPEX'!$C38"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M39": {
          "formula": "IF($B39=\"\",\"\",IF(OR($C39=\"Logiciels de conception et simulation\",$C39=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B39",
            "'DATA CAPEX'!$C39"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M40": {
          "formula": "IF($B40=\"\",\"\",IF(OR($C40=\"Logiciels de conception et simulation\",$C40=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B40",
            "'DATA CAPEX'!$C40"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M41": {
          "formula": "IF($B41=\"\",\"\",IF(OR($C41=\"Logiciels de conception et simulation\",$C41=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B41",
            "'DATA CAPEX'!$C41"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M42": {
          "formula": "IF($B42=\"\",\"\",IF(OR($C42=\"Logiciels de conception et simulation\",$C42=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B42",
            "'DATA CAPEX'!$C42"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M43": {
          "formula": "IF($B43=\"\",\"\",IF(OR($C43=\"Logiciels de conception et simulation\",$C43=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B43",
            "'DATA CAPEX'!$C43"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M44": {
          "formula": "IF($B44=\"\",\"\",IF(OR($C44=\"Logiciels de conception et simulation\",$C44=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B44",
            "'DATA CAPEX'!$C44"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M45": {
          "formula": "IF($B45=\"\",\"\",IF(OR($C45=\"Logiciels de conception et simulation\",$C45=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B45",
            "'DATA CAPEX'!$C45"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M46": {
          "formula": "IF($B46=\"\",\"\",IF(OR($C46=\"Logiciels de conception et simulation\",$C46=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B46",
            "'DATA CAPEX'!$C46"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M47": {
          "formula": "IF($B47=\"\",\"\",IF(OR($C47=\"Logiciels de conception et simulation\",$C47=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B47",
            "'DATA CAPEX'!$C47"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M48": {
          "formula": "IF($B48=\"\",\"\",IF(OR($C48=\"Logiciels de conception et simulation\",$C48=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B48",
            "'DATA CAPEX'!$C48"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M49": {
          "formula": "IF($B49=\"\",\"\",IF(OR($C49=\"Logiciels de conception et simulation\",$C49=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B49",
            "'DATA CAPEX'!$C49"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M50": {
          "formula": "IF($B50=\"\",\"\",IF(OR($C50=\"Logiciels de conception et simulation\",$C50=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B50",
            "'DATA CAPEX'!$C50"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M51": {
          "formula": "IF($B51=\"\",\"\",IF(OR($C51=\"Logiciels de conception et simulation\",$C51=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B51",
            "'DATA CAPEX'!$C51"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M52": {
          "formula": "IF($B52=\"\",\"\",IF(OR($C52=\"Logiciels de conception et simulation\",$C52=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B52",
            "'DATA CAPEX'!$C52"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M53": {
          "formula": "IF($B53=\"\",\"\",IF(OR($C53=\"Logiciels de conception et simulation\",$C53=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B53",
            "'DATA CAPEX'!$C53"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M54": {
          "formula": "IF($B54=\"\",\"\",IF(OR($C54=\"Logiciels de conception et simulation\",$C54=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B54",
            "'DATA CAPEX'!$C54"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M55": {
          "formula": "IF($B55=\"\",\"\",IF(OR($C55=\"Logiciels de conception et simulation\",$C55=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B55",
            "'DATA CAPEX'!$C55"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M56": {
          "formula": "IF($B56=\"\",\"\",IF(OR($C56=\"Logiciels de conception et simulation\",$C56=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B56",
            "'DATA CAPEX'!$C56"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M57": {
          "formula": "IF($B57=\"\",\"\",IF(OR($C57=\"Logiciels de conception et simulation\",$C57=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B57",
            "'DATA CAPEX'!$C57"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M58": {
          "formula": "IF($B58=\"\",\"\",IF(OR($C58=\"Logiciels de conception et simulation\",$C58=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B58",
            "'DATA CAPEX'!$C58"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M59": {
          "formula": "IF($B59=\"\",\"\",IF(OR($C59=\"Logiciels de conception et simulation\",$C59=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B59",
            "'DATA CAPEX'!$C59"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M60": {
          "formula": "IF($B60=\"\",\"\",IF(OR($C60=\"Logiciels de conception et simulation\",$C60=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B60",
            "'DATA CAPEX'!$C60"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M61": {
          "formula": "IF($B61=\"\",\"\",IF(OR($C61=\"Logiciels de conception et simulation\",$C61=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B61",
            "'DATA CAPEX'!$C61"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M62": {
          "formula": "IF($B62=\"\",\"\",IF(OR($C62=\"Logiciels de conception et simulation\",$C62=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B62",
            "'DATA CAPEX'!$C62"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M63": {
          "formula": "IF($B63=\"\",\"\",IF(OR($C63=\"Logiciels de conception et simulation\",$C63=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B63",
            "'DATA CAPEX'!$C63"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M64": {
          "formula": "IF($B64=\"\",\"\",IF(OR($C64=\"Logiciels de conception et simulation\",$C64=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B64",
            "'DATA CAPEX'!$C64"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M65": {
          "formula": "IF($B65=\"\",\"\",IF(OR($C65=\"Logiciels de conception et simulation\",$C65=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B65",
            "'DATA CAPEX'!$C65"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M66": {
          "formula": "IF($B66=\"\",\"\",IF(OR($C66=\"Logiciels de conception et simulation\",$C66=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B66",
            "'DATA CAPEX'!$C66"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M67": {
          "formula": "IF($B67=\"\",\"\",IF(OR($C67=\"Logiciels de conception et simulation\",$C67=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B67",
            "'DATA CAPEX'!$C67"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M68": {
          "formula": "IF($B68=\"\",\"\",IF(OR($C68=\"Logiciels de conception et simulation\",$C68=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B68",
            "'DATA CAPEX'!$C68"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M69": {
          "formula": "IF($B69=\"\",\"\",IF(OR($C69=\"Logiciels de conception et simulation\",$C69=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B69",
            "'DATA CAPEX'!$C69"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M70": {
          "formula": "IF($B70=\"\",\"\",IF(OR($C70=\"Logiciels de conception et simulation\",$C70=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B70",
            "'DATA CAPEX'!$C70"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M71": {
          "formula": "IF($B71=\"\",\"\",IF(OR($C71=\"Logiciels de conception et simulation\",$C71=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B71",
            "'DATA CAPEX'!$C71"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "M72": {
          "formula": "IF($B72=\"\",\"\",IF(OR($C72=\"Logiciels de conception et simulation\",$C72=\"Logiciels de gestion (PLM, MES, ERP)\"),\"Incorporelle\",\"Corporelle\"))",
          "references": [
            "'DATA CAPEX'!$B72",
            "'DATA CAPEX'!$C72"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_n13_n72": {
      "shape_sha256": "2aa86f6a917ac7a76126f50c4eccee935c79716a1c676f291bcf6f504738fd8d",
      "source_label": "Entretien inclus dans le loyer",
      "default_sources": {
        "N13": {
          "formula": "IF(OR($B13=\"\",$I13<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B13",
            "'DATA CAPEX'!$I13"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N14": {
          "formula": "IF(OR($B14=\"\",$I14<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B14",
            "'DATA CAPEX'!$I14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N15": {
          "formula": "IF(OR($B15=\"\",$I15<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B15",
            "'DATA CAPEX'!$I15"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N16": {
          "formula": "IF(OR($B16=\"\",$I16<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B16",
            "'DATA CAPEX'!$I16"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N17": {
          "formula": "IF(OR($B17=\"\",$I17<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B17",
            "'DATA CAPEX'!$I17"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N18": {
          "formula": "IF(OR($B18=\"\",$I18<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B18",
            "'DATA CAPEX'!$I18"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N19": {
          "formula": "IF(OR($B19=\"\",$I19<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B19",
            "'DATA CAPEX'!$I19"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N20": {
          "formula": "IF(OR($B20=\"\",$I20<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B20",
            "'DATA CAPEX'!$I20"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N21": {
          "formula": "IF(OR($B21=\"\",$I21<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B21",
            "'DATA CAPEX'!$I21"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N22": {
          "formula": "IF(OR($B22=\"\",$I22<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B22",
            "'DATA CAPEX'!$I22"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N23": {
          "formula": "IF(OR($B23=\"\",$I23<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B23",
            "'DATA CAPEX'!$I23"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N24": {
          "formula": "IF(OR($B24=\"\",$I24<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B24",
            "'DATA CAPEX'!$I24"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N25": {
          "formula": "IF(OR($B25=\"\",$I25<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B25",
            "'DATA CAPEX'!$I25"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N26": {
          "formula": "IF(OR($B26=\"\",$I26<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B26",
            "'DATA CAPEX'!$I26"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N27": {
          "formula": "IF(OR($B27=\"\",$I27<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B27",
            "'DATA CAPEX'!$I27"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N28": {
          "formula": "IF(OR($B28=\"\",$I28<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B28",
            "'DATA CAPEX'!$I28"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N29": {
          "formula": "IF(OR($B29=\"\",$I29<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B29",
            "'DATA CAPEX'!$I29"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N30": {
          "formula": "IF(OR($B30=\"\",$I30<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B30",
            "'DATA CAPEX'!$I30"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N31": {
          "formula": "IF(OR($B31=\"\",$I31<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B31",
            "'DATA CAPEX'!$I31"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N32": {
          "formula": "IF(OR($B32=\"\",$I32<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B32",
            "'DATA CAPEX'!$I32"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N33": {
          "formula": "IF(OR($B33=\"\",$I33<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B33",
            "'DATA CAPEX'!$I33"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N34": {
          "formula": "IF(OR($B34=\"\",$I34<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B34",
            "'DATA CAPEX'!$I34"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N35": {
          "formula": "IF(OR($B35=\"\",$I35<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B35",
            "'DATA CAPEX'!$I35"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N36": {
          "formula": "IF(OR($B36=\"\",$I36<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B36",
            "'DATA CAPEX'!$I36"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N37": {
          "formula": "IF(OR($B37=\"\",$I37<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B37",
            "'DATA CAPEX'!$I37"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N38": {
          "formula": "IF(OR($B38=\"\",$I38<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B38",
            "'DATA CAPEX'!$I38"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N39": {
          "formula": "IF(OR($B39=\"\",$I39<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B39",
            "'DATA CAPEX'!$I39"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N40": {
          "formula": "IF(OR($B40=\"\",$I40<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B40",
            "'DATA CAPEX'!$I40"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N41": {
          "formula": "IF(OR($B41=\"\",$I41<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B41",
            "'DATA CAPEX'!$I41"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N42": {
          "formula": "IF(OR($B42=\"\",$I42<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B42",
            "'DATA CAPEX'!$I42"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N43": {
          "formula": "IF(OR($B43=\"\",$I43<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B43",
            "'DATA CAPEX'!$I43"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N44": {
          "formula": "IF(OR($B44=\"\",$I44<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B44",
            "'DATA CAPEX'!$I44"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N45": {
          "formula": "IF(OR($B45=\"\",$I45<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B45",
            "'DATA CAPEX'!$I45"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N46": {
          "formula": "IF(OR($B46=\"\",$I46<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B46",
            "'DATA CAPEX'!$I46"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N47": {
          "formula": "IF(OR($B47=\"\",$I47<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B47",
            "'DATA CAPEX'!$I47"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N48": {
          "formula": "IF(OR($B48=\"\",$I48<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B48",
            "'DATA CAPEX'!$I48"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N49": {
          "formula": "IF(OR($B49=\"\",$I49<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B49",
            "'DATA CAPEX'!$I49"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N50": {
          "formula": "IF(OR($B50=\"\",$I50<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B50",
            "'DATA CAPEX'!$I50"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N51": {
          "formula": "IF(OR($B51=\"\",$I51<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B51",
            "'DATA CAPEX'!$I51"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N52": {
          "formula": "IF(OR($B52=\"\",$I52<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B52",
            "'DATA CAPEX'!$I52"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N53": {
          "formula": "IF(OR($B53=\"\",$I53<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B53",
            "'DATA CAPEX'!$I53"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N54": {
          "formula": "IF(OR($B54=\"\",$I54<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B54",
            "'DATA CAPEX'!$I54"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N55": {
          "formula": "IF(OR($B55=\"\",$I55<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B55",
            "'DATA CAPEX'!$I55"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N56": {
          "formula": "IF(OR($B56=\"\",$I56<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B56",
            "'DATA CAPEX'!$I56"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N57": {
          "formula": "IF(OR($B57=\"\",$I57<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B57",
            "'DATA CAPEX'!$I57"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N58": {
          "formula": "IF(OR($B58=\"\",$I58<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B58",
            "'DATA CAPEX'!$I58"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N59": {
          "formula": "IF(OR($B59=\"\",$I59<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B59",
            "'DATA CAPEX'!$I59"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N60": {
          "formula": "IF(OR($B60=\"\",$I60<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B60",
            "'DATA CAPEX'!$I60"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N61": {
          "formula": "IF(OR($B61=\"\",$I61<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B61",
            "'DATA CAPEX'!$I61"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N62": {
          "formula": "IF(OR($B62=\"\",$I62<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B62",
            "'DATA CAPEX'!$I62"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N63": {
          "formula": "IF(OR($B63=\"\",$I63<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B63",
            "'DATA CAPEX'!$I63"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N64": {
          "formula": "IF(OR($B64=\"\",$I64<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B64",
            "'DATA CAPEX'!$I64"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N65": {
          "formula": "IF(OR($B65=\"\",$I65<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B65",
            "'DATA CAPEX'!$I65"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N66": {
          "formula": "IF(OR($B66=\"\",$I66<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B66",
            "'DATA CAPEX'!$I66"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N67": {
          "formula": "IF(OR($B67=\"\",$I67<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B67",
            "'DATA CAPEX'!$I67"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N68": {
          "formula": "IF(OR($B68=\"\",$I68<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B68",
            "'DATA CAPEX'!$I68"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N69": {
          "formula": "IF(OR($B69=\"\",$I69<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B69",
            "'DATA CAPEX'!$I69"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N70": {
          "formula": "IF(OR($B70=\"\",$I70<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B70",
            "'DATA CAPEX'!$I70"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N71": {
          "formula": "IF(OR($B71=\"\",$I71<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B71",
            "'DATA CAPEX'!$I71"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "N72": {
          "formula": "IF(OR($B72=\"\",$I72<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B72",
            "'DATA CAPEX'!$I72"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_o13_o72": {
      "shape_sha256": "bcae5411ed0e885049cce53786b9d03a8b8975965218a63ebe480d69aac732d4",
      "source_label": "Assurance incluse dans le loyer",
      "default_sources": {
        "O13": {
          "formula": "IF(OR($B13=\"\",$I13<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B13",
            "'DATA CAPEX'!$I13"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O14": {
          "formula": "IF(OR($B14=\"\",$I14<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B14",
            "'DATA CAPEX'!$I14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O15": {
          "formula": "IF(OR($B15=\"\",$I15<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B15",
            "'DATA CAPEX'!$I15"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O16": {
          "formula": "IF(OR($B16=\"\",$I16<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B16",
            "'DATA CAPEX'!$I16"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O17": {
          "formula": "IF(OR($B17=\"\",$I17<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B17",
            "'DATA CAPEX'!$I17"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O18": {
          "formula": "IF(OR($B18=\"\",$I18<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B18",
            "'DATA CAPEX'!$I18"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O19": {
          "formula": "IF(OR($B19=\"\",$I19<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B19",
            "'DATA CAPEX'!$I19"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O20": {
          "formula": "IF(OR($B20=\"\",$I20<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B20",
            "'DATA CAPEX'!$I20"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O21": {
          "formula": "IF(OR($B21=\"\",$I21<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B21",
            "'DATA CAPEX'!$I21"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O22": {
          "formula": "IF(OR($B22=\"\",$I22<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B22",
            "'DATA CAPEX'!$I22"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O23": {
          "formula": "IF(OR($B23=\"\",$I23<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B23",
            "'DATA CAPEX'!$I23"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O24": {
          "formula": "IF(OR($B24=\"\",$I24<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B24",
            "'DATA CAPEX'!$I24"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O25": {
          "formula": "IF(OR($B25=\"\",$I25<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B25",
            "'DATA CAPEX'!$I25"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O26": {
          "formula": "IF(OR($B26=\"\",$I26<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B26",
            "'DATA CAPEX'!$I26"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O27": {
          "formula": "IF(OR($B27=\"\",$I27<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B27",
            "'DATA CAPEX'!$I27"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O28": {
          "formula": "IF(OR($B28=\"\",$I28<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B28",
            "'DATA CAPEX'!$I28"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O29": {
          "formula": "IF(OR($B29=\"\",$I29<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B29",
            "'DATA CAPEX'!$I29"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O30": {
          "formula": "IF(OR($B30=\"\",$I30<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B30",
            "'DATA CAPEX'!$I30"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O31": {
          "formula": "IF(OR($B31=\"\",$I31<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B31",
            "'DATA CAPEX'!$I31"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O32": {
          "formula": "IF(OR($B32=\"\",$I32<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B32",
            "'DATA CAPEX'!$I32"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O33": {
          "formula": "IF(OR($B33=\"\",$I33<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B33",
            "'DATA CAPEX'!$I33"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O34": {
          "formula": "IF(OR($B34=\"\",$I34<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B34",
            "'DATA CAPEX'!$I34"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O35": {
          "formula": "IF(OR($B35=\"\",$I35<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B35",
            "'DATA CAPEX'!$I35"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O36": {
          "formula": "IF(OR($B36=\"\",$I36<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B36",
            "'DATA CAPEX'!$I36"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O37": {
          "formula": "IF(OR($B37=\"\",$I37<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B37",
            "'DATA CAPEX'!$I37"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O38": {
          "formula": "IF(OR($B38=\"\",$I38<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B38",
            "'DATA CAPEX'!$I38"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O39": {
          "formula": "IF(OR($B39=\"\",$I39<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B39",
            "'DATA CAPEX'!$I39"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O40": {
          "formula": "IF(OR($B40=\"\",$I40<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B40",
            "'DATA CAPEX'!$I40"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O41": {
          "formula": "IF(OR($B41=\"\",$I41<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B41",
            "'DATA CAPEX'!$I41"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O42": {
          "formula": "IF(OR($B42=\"\",$I42<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B42",
            "'DATA CAPEX'!$I42"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O43": {
          "formula": "IF(OR($B43=\"\",$I43<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B43",
            "'DATA CAPEX'!$I43"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O44": {
          "formula": "IF(OR($B44=\"\",$I44<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B44",
            "'DATA CAPEX'!$I44"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O45": {
          "formula": "IF(OR($B45=\"\",$I45<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B45",
            "'DATA CAPEX'!$I45"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O46": {
          "formula": "IF(OR($B46=\"\",$I46<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B46",
            "'DATA CAPEX'!$I46"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O47": {
          "formula": "IF(OR($B47=\"\",$I47<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B47",
            "'DATA CAPEX'!$I47"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O48": {
          "formula": "IF(OR($B48=\"\",$I48<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B48",
            "'DATA CAPEX'!$I48"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O49": {
          "formula": "IF(OR($B49=\"\",$I49<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B49",
            "'DATA CAPEX'!$I49"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O50": {
          "formula": "IF(OR($B50=\"\",$I50<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B50",
            "'DATA CAPEX'!$I50"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O51": {
          "formula": "IF(OR($B51=\"\",$I51<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B51",
            "'DATA CAPEX'!$I51"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O52": {
          "formula": "IF(OR($B52=\"\",$I52<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B52",
            "'DATA CAPEX'!$I52"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O53": {
          "formula": "IF(OR($B53=\"\",$I53<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B53",
            "'DATA CAPEX'!$I53"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O54": {
          "formula": "IF(OR($B54=\"\",$I54<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B54",
            "'DATA CAPEX'!$I54"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O55": {
          "formula": "IF(OR($B55=\"\",$I55<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B55",
            "'DATA CAPEX'!$I55"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O56": {
          "formula": "IF(OR($B56=\"\",$I56<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B56",
            "'DATA CAPEX'!$I56"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O57": {
          "formula": "IF(OR($B57=\"\",$I57<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B57",
            "'DATA CAPEX'!$I57"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O58": {
          "formula": "IF(OR($B58=\"\",$I58<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B58",
            "'DATA CAPEX'!$I58"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O59": {
          "formula": "IF(OR($B59=\"\",$I59<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B59",
            "'DATA CAPEX'!$I59"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O60": {
          "formula": "IF(OR($B60=\"\",$I60<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B60",
            "'DATA CAPEX'!$I60"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O61": {
          "formula": "IF(OR($B61=\"\",$I61<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B61",
            "'DATA CAPEX'!$I61"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O62": {
          "formula": "IF(OR($B62=\"\",$I62<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B62",
            "'DATA CAPEX'!$I62"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O63": {
          "formula": "IF(OR($B63=\"\",$I63<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B63",
            "'DATA CAPEX'!$I63"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O64": {
          "formula": "IF(OR($B64=\"\",$I64<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B64",
            "'DATA CAPEX'!$I64"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O65": {
          "formula": "IF(OR($B65=\"\",$I65<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B65",
            "'DATA CAPEX'!$I65"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O66": {
          "formula": "IF(OR($B66=\"\",$I66<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B66",
            "'DATA CAPEX'!$I66"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O67": {
          "formula": "IF(OR($B67=\"\",$I67<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B67",
            "'DATA CAPEX'!$I67"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O68": {
          "formula": "IF(OR($B68=\"\",$I68<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B68",
            "'DATA CAPEX'!$I68"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O69": {
          "formula": "IF(OR($B69=\"\",$I69<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B69",
            "'DATA CAPEX'!$I69"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O70": {
          "formula": "IF(OR($B70=\"\",$I70<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B70",
            "'DATA CAPEX'!$I70"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O71": {
          "formula": "IF(OR($B71=\"\",$I71<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B71",
            "'DATA CAPEX'!$I71"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "O72": {
          "formula": "IF(OR($B72=\"\",$I72<>\"Crédit-bail\"),\"\",\"Non\")",
          "references": [
            "'DATA CAPEX'!$B72",
            "'DATA CAPEX'!$I72"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "data_capex_p13_p72": {
      "shape_sha256": "2cbc70cf92237eeefeccbfefdce9915b59ad9907049d6c083881a3a8c67818b2",
      "source_label": "Dernière date d’exploitation du bien loué",
      "default_sources": {
        "P13": {
          "formula": "IF(OR($B13=\"\",$I13<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E13),N($E13)>0,ISNUMBER($J13),N($J13)>0,ABS(N($J13)*12-ROUND(N($J13)*12,0))<0.00000001),EDATE(DATE(YEAR($E13),MONTH($E13),1),ROUND(N($J13)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B13",
            "'DATA CAPEX'!$I13",
            "'DATA CAPEX'!$E13",
            "'DATA CAPEX'!$J13"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P14": {
          "formula": "IF(OR($B14=\"\",$I14<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E14),N($E14)>0,ISNUMBER($J14),N($J14)>0,ABS(N($J14)*12-ROUND(N($J14)*12,0))<0.00000001),EDATE(DATE(YEAR($E14),MONTH($E14),1),ROUND(N($J14)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B14",
            "'DATA CAPEX'!$I14",
            "'DATA CAPEX'!$E14",
            "'DATA CAPEX'!$J14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P15": {
          "formula": "IF(OR($B15=\"\",$I15<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E15),N($E15)>0,ISNUMBER($J15),N($J15)>0,ABS(N($J15)*12-ROUND(N($J15)*12,0))<0.00000001),EDATE(DATE(YEAR($E15),MONTH($E15),1),ROUND(N($J15)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B15",
            "'DATA CAPEX'!$I15",
            "'DATA CAPEX'!$E15",
            "'DATA CAPEX'!$J15"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P16": {
          "formula": "IF(OR($B16=\"\",$I16<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E16),N($E16)>0,ISNUMBER($J16),N($J16)>0,ABS(N($J16)*12-ROUND(N($J16)*12,0))<0.00000001),EDATE(DATE(YEAR($E16),MONTH($E16),1),ROUND(N($J16)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B16",
            "'DATA CAPEX'!$I16",
            "'DATA CAPEX'!$E16",
            "'DATA CAPEX'!$J16"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P17": {
          "formula": "IF(OR($B17=\"\",$I17<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E17),N($E17)>0,ISNUMBER($J17),N($J17)>0,ABS(N($J17)*12-ROUND(N($J17)*12,0))<0.00000001),EDATE(DATE(YEAR($E17),MONTH($E17),1),ROUND(N($J17)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B17",
            "'DATA CAPEX'!$I17",
            "'DATA CAPEX'!$E17",
            "'DATA CAPEX'!$J17"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P18": {
          "formula": "IF(OR($B18=\"\",$I18<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E18),N($E18)>0,ISNUMBER($J18),N($J18)>0,ABS(N($J18)*12-ROUND(N($J18)*12,0))<0.00000001),EDATE(DATE(YEAR($E18),MONTH($E18),1),ROUND(N($J18)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B18",
            "'DATA CAPEX'!$I18",
            "'DATA CAPEX'!$E18",
            "'DATA CAPEX'!$J18"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P19": {
          "formula": "IF(OR($B19=\"\",$I19<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E19),N($E19)>0,ISNUMBER($J19),N($J19)>0,ABS(N($J19)*12-ROUND(N($J19)*12,0))<0.00000001),EDATE(DATE(YEAR($E19),MONTH($E19),1),ROUND(N($J19)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B19",
            "'DATA CAPEX'!$I19",
            "'DATA CAPEX'!$E19",
            "'DATA CAPEX'!$J19"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P20": {
          "formula": "IF(OR($B20=\"\",$I20<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E20),N($E20)>0,ISNUMBER($J20),N($J20)>0,ABS(N($J20)*12-ROUND(N($J20)*12,0))<0.00000001),EDATE(DATE(YEAR($E20),MONTH($E20),1),ROUND(N($J20)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B20",
            "'DATA CAPEX'!$I20",
            "'DATA CAPEX'!$E20",
            "'DATA CAPEX'!$J20"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P21": {
          "formula": "IF(OR($B21=\"\",$I21<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E21),N($E21)>0,ISNUMBER($J21),N($J21)>0,ABS(N($J21)*12-ROUND(N($J21)*12,0))<0.00000001),EDATE(DATE(YEAR($E21),MONTH($E21),1),ROUND(N($J21)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B21",
            "'DATA CAPEX'!$I21",
            "'DATA CAPEX'!$E21",
            "'DATA CAPEX'!$J21"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P22": {
          "formula": "IF(OR($B22=\"\",$I22<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E22),N($E22)>0,ISNUMBER($J22),N($J22)>0,ABS(N($J22)*12-ROUND(N($J22)*12,0))<0.00000001),EDATE(DATE(YEAR($E22),MONTH($E22),1),ROUND(N($J22)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B22",
            "'DATA CAPEX'!$I22",
            "'DATA CAPEX'!$E22",
            "'DATA CAPEX'!$J22"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P23": {
          "formula": "IF(OR($B23=\"\",$I23<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E23),N($E23)>0,ISNUMBER($J23),N($J23)>0,ABS(N($J23)*12-ROUND(N($J23)*12,0))<0.00000001),EDATE(DATE(YEAR($E23),MONTH($E23),1),ROUND(N($J23)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B23",
            "'DATA CAPEX'!$I23",
            "'DATA CAPEX'!$E23",
            "'DATA CAPEX'!$J23"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P24": {
          "formula": "IF(OR($B24=\"\",$I24<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E24),N($E24)>0,ISNUMBER($J24),N($J24)>0,ABS(N($J24)*12-ROUND(N($J24)*12,0))<0.00000001),EDATE(DATE(YEAR($E24),MONTH($E24),1),ROUND(N($J24)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B24",
            "'DATA CAPEX'!$I24",
            "'DATA CAPEX'!$E24",
            "'DATA CAPEX'!$J24"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P25": {
          "formula": "IF(OR($B25=\"\",$I25<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E25),N($E25)>0,ISNUMBER($J25),N($J25)>0,ABS(N($J25)*12-ROUND(N($J25)*12,0))<0.00000001),EDATE(DATE(YEAR($E25),MONTH($E25),1),ROUND(N($J25)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B25",
            "'DATA CAPEX'!$I25",
            "'DATA CAPEX'!$E25",
            "'DATA CAPEX'!$J25"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P26": {
          "formula": "IF(OR($B26=\"\",$I26<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E26),N($E26)>0,ISNUMBER($J26),N($J26)>0,ABS(N($J26)*12-ROUND(N($J26)*12,0))<0.00000001),EDATE(DATE(YEAR($E26),MONTH($E26),1),ROUND(N($J26)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B26",
            "'DATA CAPEX'!$I26",
            "'DATA CAPEX'!$E26",
            "'DATA CAPEX'!$J26"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P27": {
          "formula": "IF(OR($B27=\"\",$I27<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E27),N($E27)>0,ISNUMBER($J27),N($J27)>0,ABS(N($J27)*12-ROUND(N($J27)*12,0))<0.00000001),EDATE(DATE(YEAR($E27),MONTH($E27),1),ROUND(N($J27)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B27",
            "'DATA CAPEX'!$I27",
            "'DATA CAPEX'!$E27",
            "'DATA CAPEX'!$J27"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P28": {
          "formula": "IF(OR($B28=\"\",$I28<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E28),N($E28)>0,ISNUMBER($J28),N($J28)>0,ABS(N($J28)*12-ROUND(N($J28)*12,0))<0.00000001),EDATE(DATE(YEAR($E28),MONTH($E28),1),ROUND(N($J28)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B28",
            "'DATA CAPEX'!$I28",
            "'DATA CAPEX'!$E28",
            "'DATA CAPEX'!$J28"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P29": {
          "formula": "IF(OR($B29=\"\",$I29<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E29),N($E29)>0,ISNUMBER($J29),N($J29)>0,ABS(N($J29)*12-ROUND(N($J29)*12,0))<0.00000001),EDATE(DATE(YEAR($E29),MONTH($E29),1),ROUND(N($J29)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B29",
            "'DATA CAPEX'!$I29",
            "'DATA CAPEX'!$E29",
            "'DATA CAPEX'!$J29"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P30": {
          "formula": "IF(OR($B30=\"\",$I30<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E30),N($E30)>0,ISNUMBER($J30),N($J30)>0,ABS(N($J30)*12-ROUND(N($J30)*12,0))<0.00000001),EDATE(DATE(YEAR($E30),MONTH($E30),1),ROUND(N($J30)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B30",
            "'DATA CAPEX'!$I30",
            "'DATA CAPEX'!$E30",
            "'DATA CAPEX'!$J30"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P31": {
          "formula": "IF(OR($B31=\"\",$I31<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E31),N($E31)>0,ISNUMBER($J31),N($J31)>0,ABS(N($J31)*12-ROUND(N($J31)*12,0))<0.00000001),EDATE(DATE(YEAR($E31),MONTH($E31),1),ROUND(N($J31)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B31",
            "'DATA CAPEX'!$I31",
            "'DATA CAPEX'!$E31",
            "'DATA CAPEX'!$J31"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P32": {
          "formula": "IF(OR($B32=\"\",$I32<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E32),N($E32)>0,ISNUMBER($J32),N($J32)>0,ABS(N($J32)*12-ROUND(N($J32)*12,0))<0.00000001),EDATE(DATE(YEAR($E32),MONTH($E32),1),ROUND(N($J32)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B32",
            "'DATA CAPEX'!$I32",
            "'DATA CAPEX'!$E32",
            "'DATA CAPEX'!$J32"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P33": {
          "formula": "IF(OR($B33=\"\",$I33<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E33),N($E33)>0,ISNUMBER($J33),N($J33)>0,ABS(N($J33)*12-ROUND(N($J33)*12,0))<0.00000001),EDATE(DATE(YEAR($E33),MONTH($E33),1),ROUND(N($J33)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B33",
            "'DATA CAPEX'!$I33",
            "'DATA CAPEX'!$E33",
            "'DATA CAPEX'!$J33"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P34": {
          "formula": "IF(OR($B34=\"\",$I34<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E34),N($E34)>0,ISNUMBER($J34),N($J34)>0,ABS(N($J34)*12-ROUND(N($J34)*12,0))<0.00000001),EDATE(DATE(YEAR($E34),MONTH($E34),1),ROUND(N($J34)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B34",
            "'DATA CAPEX'!$I34",
            "'DATA CAPEX'!$E34",
            "'DATA CAPEX'!$J34"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P35": {
          "formula": "IF(OR($B35=\"\",$I35<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E35),N($E35)>0,ISNUMBER($J35),N($J35)>0,ABS(N($J35)*12-ROUND(N($J35)*12,0))<0.00000001),EDATE(DATE(YEAR($E35),MONTH($E35),1),ROUND(N($J35)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B35",
            "'DATA CAPEX'!$I35",
            "'DATA CAPEX'!$E35",
            "'DATA CAPEX'!$J35"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P36": {
          "formula": "IF(OR($B36=\"\",$I36<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E36),N($E36)>0,ISNUMBER($J36),N($J36)>0,ABS(N($J36)*12-ROUND(N($J36)*12,0))<0.00000001),EDATE(DATE(YEAR($E36),MONTH($E36),1),ROUND(N($J36)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B36",
            "'DATA CAPEX'!$I36",
            "'DATA CAPEX'!$E36",
            "'DATA CAPEX'!$J36"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P37": {
          "formula": "IF(OR($B37=\"\",$I37<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E37),N($E37)>0,ISNUMBER($J37),N($J37)>0,ABS(N($J37)*12-ROUND(N($J37)*12,0))<0.00000001),EDATE(DATE(YEAR($E37),MONTH($E37),1),ROUND(N($J37)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B37",
            "'DATA CAPEX'!$I37",
            "'DATA CAPEX'!$E37",
            "'DATA CAPEX'!$J37"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P38": {
          "formula": "IF(OR($B38=\"\",$I38<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E38),N($E38)>0,ISNUMBER($J38),N($J38)>0,ABS(N($J38)*12-ROUND(N($J38)*12,0))<0.00000001),EDATE(DATE(YEAR($E38),MONTH($E38),1),ROUND(N($J38)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B38",
            "'DATA CAPEX'!$I38",
            "'DATA CAPEX'!$E38",
            "'DATA CAPEX'!$J38"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P39": {
          "formula": "IF(OR($B39=\"\",$I39<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E39),N($E39)>0,ISNUMBER($J39),N($J39)>0,ABS(N($J39)*12-ROUND(N($J39)*12,0))<0.00000001),EDATE(DATE(YEAR($E39),MONTH($E39),1),ROUND(N($J39)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B39",
            "'DATA CAPEX'!$I39",
            "'DATA CAPEX'!$E39",
            "'DATA CAPEX'!$J39"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P40": {
          "formula": "IF(OR($B40=\"\",$I40<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E40),N($E40)>0,ISNUMBER($J40),N($J40)>0,ABS(N($J40)*12-ROUND(N($J40)*12,0))<0.00000001),EDATE(DATE(YEAR($E40),MONTH($E40),1),ROUND(N($J40)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B40",
            "'DATA CAPEX'!$I40",
            "'DATA CAPEX'!$E40",
            "'DATA CAPEX'!$J40"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P41": {
          "formula": "IF(OR($B41=\"\",$I41<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E41),N($E41)>0,ISNUMBER($J41),N($J41)>0,ABS(N($J41)*12-ROUND(N($J41)*12,0))<0.00000001),EDATE(DATE(YEAR($E41),MONTH($E41),1),ROUND(N($J41)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B41",
            "'DATA CAPEX'!$I41",
            "'DATA CAPEX'!$E41",
            "'DATA CAPEX'!$J41"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P42": {
          "formula": "IF(OR($B42=\"\",$I42<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E42),N($E42)>0,ISNUMBER($J42),N($J42)>0,ABS(N($J42)*12-ROUND(N($J42)*12,0))<0.00000001),EDATE(DATE(YEAR($E42),MONTH($E42),1),ROUND(N($J42)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B42",
            "'DATA CAPEX'!$I42",
            "'DATA CAPEX'!$E42",
            "'DATA CAPEX'!$J42"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P43": {
          "formula": "IF(OR($B43=\"\",$I43<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E43),N($E43)>0,ISNUMBER($J43),N($J43)>0,ABS(N($J43)*12-ROUND(N($J43)*12,0))<0.00000001),EDATE(DATE(YEAR($E43),MONTH($E43),1),ROUND(N($J43)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B43",
            "'DATA CAPEX'!$I43",
            "'DATA CAPEX'!$E43",
            "'DATA CAPEX'!$J43"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P44": {
          "formula": "IF(OR($B44=\"\",$I44<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E44),N($E44)>0,ISNUMBER($J44),N($J44)>0,ABS(N($J44)*12-ROUND(N($J44)*12,0))<0.00000001),EDATE(DATE(YEAR($E44),MONTH($E44),1),ROUND(N($J44)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B44",
            "'DATA CAPEX'!$I44",
            "'DATA CAPEX'!$E44",
            "'DATA CAPEX'!$J44"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P45": {
          "formula": "IF(OR($B45=\"\",$I45<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E45),N($E45)>0,ISNUMBER($J45),N($J45)>0,ABS(N($J45)*12-ROUND(N($J45)*12,0))<0.00000001),EDATE(DATE(YEAR($E45),MONTH($E45),1),ROUND(N($J45)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B45",
            "'DATA CAPEX'!$I45",
            "'DATA CAPEX'!$E45",
            "'DATA CAPEX'!$J45"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P46": {
          "formula": "IF(OR($B46=\"\",$I46<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E46),N($E46)>0,ISNUMBER($J46),N($J46)>0,ABS(N($J46)*12-ROUND(N($J46)*12,0))<0.00000001),EDATE(DATE(YEAR($E46),MONTH($E46),1),ROUND(N($J46)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B46",
            "'DATA CAPEX'!$I46",
            "'DATA CAPEX'!$E46",
            "'DATA CAPEX'!$J46"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P47": {
          "formula": "IF(OR($B47=\"\",$I47<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E47),N($E47)>0,ISNUMBER($J47),N($J47)>0,ABS(N($J47)*12-ROUND(N($J47)*12,0))<0.00000001),EDATE(DATE(YEAR($E47),MONTH($E47),1),ROUND(N($J47)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B47",
            "'DATA CAPEX'!$I47",
            "'DATA CAPEX'!$E47",
            "'DATA CAPEX'!$J47"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P48": {
          "formula": "IF(OR($B48=\"\",$I48<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E48),N($E48)>0,ISNUMBER($J48),N($J48)>0,ABS(N($J48)*12-ROUND(N($J48)*12,0))<0.00000001),EDATE(DATE(YEAR($E48),MONTH($E48),1),ROUND(N($J48)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B48",
            "'DATA CAPEX'!$I48",
            "'DATA CAPEX'!$E48",
            "'DATA CAPEX'!$J48"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P49": {
          "formula": "IF(OR($B49=\"\",$I49<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E49),N($E49)>0,ISNUMBER($J49),N($J49)>0,ABS(N($J49)*12-ROUND(N($J49)*12,0))<0.00000001),EDATE(DATE(YEAR($E49),MONTH($E49),1),ROUND(N($J49)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B49",
            "'DATA CAPEX'!$I49",
            "'DATA CAPEX'!$E49",
            "'DATA CAPEX'!$J49"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P50": {
          "formula": "IF(OR($B50=\"\",$I50<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E50),N($E50)>0,ISNUMBER($J50),N($J50)>0,ABS(N($J50)*12-ROUND(N($J50)*12,0))<0.00000001),EDATE(DATE(YEAR($E50),MONTH($E50),1),ROUND(N($J50)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B50",
            "'DATA CAPEX'!$I50",
            "'DATA CAPEX'!$E50",
            "'DATA CAPEX'!$J50"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P51": {
          "formula": "IF(OR($B51=\"\",$I51<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E51),N($E51)>0,ISNUMBER($J51),N($J51)>0,ABS(N($J51)*12-ROUND(N($J51)*12,0))<0.00000001),EDATE(DATE(YEAR($E51),MONTH($E51),1),ROUND(N($J51)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B51",
            "'DATA CAPEX'!$I51",
            "'DATA CAPEX'!$E51",
            "'DATA CAPEX'!$J51"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P52": {
          "formula": "IF(OR($B52=\"\",$I52<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E52),N($E52)>0,ISNUMBER($J52),N($J52)>0,ABS(N($J52)*12-ROUND(N($J52)*12,0))<0.00000001),EDATE(DATE(YEAR($E52),MONTH($E52),1),ROUND(N($J52)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B52",
            "'DATA CAPEX'!$I52",
            "'DATA CAPEX'!$E52",
            "'DATA CAPEX'!$J52"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P53": {
          "formula": "IF(OR($B53=\"\",$I53<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E53),N($E53)>0,ISNUMBER($J53),N($J53)>0,ABS(N($J53)*12-ROUND(N($J53)*12,0))<0.00000001),EDATE(DATE(YEAR($E53),MONTH($E53),1),ROUND(N($J53)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B53",
            "'DATA CAPEX'!$I53",
            "'DATA CAPEX'!$E53",
            "'DATA CAPEX'!$J53"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P54": {
          "formula": "IF(OR($B54=\"\",$I54<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E54),N($E54)>0,ISNUMBER($J54),N($J54)>0,ABS(N($J54)*12-ROUND(N($J54)*12,0))<0.00000001),EDATE(DATE(YEAR($E54),MONTH($E54),1),ROUND(N($J54)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B54",
            "'DATA CAPEX'!$I54",
            "'DATA CAPEX'!$E54",
            "'DATA CAPEX'!$J54"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P55": {
          "formula": "IF(OR($B55=\"\",$I55<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E55),N($E55)>0,ISNUMBER($J55),N($J55)>0,ABS(N($J55)*12-ROUND(N($J55)*12,0))<0.00000001),EDATE(DATE(YEAR($E55),MONTH($E55),1),ROUND(N($J55)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B55",
            "'DATA CAPEX'!$I55",
            "'DATA CAPEX'!$E55",
            "'DATA CAPEX'!$J55"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P56": {
          "formula": "IF(OR($B56=\"\",$I56<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E56),N($E56)>0,ISNUMBER($J56),N($J56)>0,ABS(N($J56)*12-ROUND(N($J56)*12,0))<0.00000001),EDATE(DATE(YEAR($E56),MONTH($E56),1),ROUND(N($J56)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B56",
            "'DATA CAPEX'!$I56",
            "'DATA CAPEX'!$E56",
            "'DATA CAPEX'!$J56"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P57": {
          "formula": "IF(OR($B57=\"\",$I57<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E57),N($E57)>0,ISNUMBER($J57),N($J57)>0,ABS(N($J57)*12-ROUND(N($J57)*12,0))<0.00000001),EDATE(DATE(YEAR($E57),MONTH($E57),1),ROUND(N($J57)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B57",
            "'DATA CAPEX'!$I57",
            "'DATA CAPEX'!$E57",
            "'DATA CAPEX'!$J57"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P58": {
          "formula": "IF(OR($B58=\"\",$I58<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E58),N($E58)>0,ISNUMBER($J58),N($J58)>0,ABS(N($J58)*12-ROUND(N($J58)*12,0))<0.00000001),EDATE(DATE(YEAR($E58),MONTH($E58),1),ROUND(N($J58)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B58",
            "'DATA CAPEX'!$I58",
            "'DATA CAPEX'!$E58",
            "'DATA CAPEX'!$J58"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P59": {
          "formula": "IF(OR($B59=\"\",$I59<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E59),N($E59)>0,ISNUMBER($J59),N($J59)>0,ABS(N($J59)*12-ROUND(N($J59)*12,0))<0.00000001),EDATE(DATE(YEAR($E59),MONTH($E59),1),ROUND(N($J59)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B59",
            "'DATA CAPEX'!$I59",
            "'DATA CAPEX'!$E59",
            "'DATA CAPEX'!$J59"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P60": {
          "formula": "IF(OR($B60=\"\",$I60<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E60),N($E60)>0,ISNUMBER($J60),N($J60)>0,ABS(N($J60)*12-ROUND(N($J60)*12,0))<0.00000001),EDATE(DATE(YEAR($E60),MONTH($E60),1),ROUND(N($J60)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B60",
            "'DATA CAPEX'!$I60",
            "'DATA CAPEX'!$E60",
            "'DATA CAPEX'!$J60"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P61": {
          "formula": "IF(OR($B61=\"\",$I61<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E61),N($E61)>0,ISNUMBER($J61),N($J61)>0,ABS(N($J61)*12-ROUND(N($J61)*12,0))<0.00000001),EDATE(DATE(YEAR($E61),MONTH($E61),1),ROUND(N($J61)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B61",
            "'DATA CAPEX'!$I61",
            "'DATA CAPEX'!$E61",
            "'DATA CAPEX'!$J61"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P62": {
          "formula": "IF(OR($B62=\"\",$I62<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E62),N($E62)>0,ISNUMBER($J62),N($J62)>0,ABS(N($J62)*12-ROUND(N($J62)*12,0))<0.00000001),EDATE(DATE(YEAR($E62),MONTH($E62),1),ROUND(N($J62)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B62",
            "'DATA CAPEX'!$I62",
            "'DATA CAPEX'!$E62",
            "'DATA CAPEX'!$J62"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P63": {
          "formula": "IF(OR($B63=\"\",$I63<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E63),N($E63)>0,ISNUMBER($J63),N($J63)>0,ABS(N($J63)*12-ROUND(N($J63)*12,0))<0.00000001),EDATE(DATE(YEAR($E63),MONTH($E63),1),ROUND(N($J63)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B63",
            "'DATA CAPEX'!$I63",
            "'DATA CAPEX'!$E63",
            "'DATA CAPEX'!$J63"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P64": {
          "formula": "IF(OR($B64=\"\",$I64<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E64),N($E64)>0,ISNUMBER($J64),N($J64)>0,ABS(N($J64)*12-ROUND(N($J64)*12,0))<0.00000001),EDATE(DATE(YEAR($E64),MONTH($E64),1),ROUND(N($J64)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B64",
            "'DATA CAPEX'!$I64",
            "'DATA CAPEX'!$E64",
            "'DATA CAPEX'!$J64"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P65": {
          "formula": "IF(OR($B65=\"\",$I65<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E65),N($E65)>0,ISNUMBER($J65),N($J65)>0,ABS(N($J65)*12-ROUND(N($J65)*12,0))<0.00000001),EDATE(DATE(YEAR($E65),MONTH($E65),1),ROUND(N($J65)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B65",
            "'DATA CAPEX'!$I65",
            "'DATA CAPEX'!$E65",
            "'DATA CAPEX'!$J65"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P66": {
          "formula": "IF(OR($B66=\"\",$I66<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E66),N($E66)>0,ISNUMBER($J66),N($J66)>0,ABS(N($J66)*12-ROUND(N($J66)*12,0))<0.00000001),EDATE(DATE(YEAR($E66),MONTH($E66),1),ROUND(N($J66)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B66",
            "'DATA CAPEX'!$I66",
            "'DATA CAPEX'!$E66",
            "'DATA CAPEX'!$J66"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P67": {
          "formula": "IF(OR($B67=\"\",$I67<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E67),N($E67)>0,ISNUMBER($J67),N($J67)>0,ABS(N($J67)*12-ROUND(N($J67)*12,0))<0.00000001),EDATE(DATE(YEAR($E67),MONTH($E67),1),ROUND(N($J67)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B67",
            "'DATA CAPEX'!$I67",
            "'DATA CAPEX'!$E67",
            "'DATA CAPEX'!$J67"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P68": {
          "formula": "IF(OR($B68=\"\",$I68<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E68),N($E68)>0,ISNUMBER($J68),N($J68)>0,ABS(N($J68)*12-ROUND(N($J68)*12,0))<0.00000001),EDATE(DATE(YEAR($E68),MONTH($E68),1),ROUND(N($J68)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B68",
            "'DATA CAPEX'!$I68",
            "'DATA CAPEX'!$E68",
            "'DATA CAPEX'!$J68"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P69": {
          "formula": "IF(OR($B69=\"\",$I69<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E69),N($E69)>0,ISNUMBER($J69),N($J69)>0,ABS(N($J69)*12-ROUND(N($J69)*12,0))<0.00000001),EDATE(DATE(YEAR($E69),MONTH($E69),1),ROUND(N($J69)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B69",
            "'DATA CAPEX'!$I69",
            "'DATA CAPEX'!$E69",
            "'DATA CAPEX'!$J69"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P70": {
          "formula": "IF(OR($B70=\"\",$I70<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E70),N($E70)>0,ISNUMBER($J70),N($J70)>0,ABS(N($J70)*12-ROUND(N($J70)*12,0))<0.00000001),EDATE(DATE(YEAR($E70),MONTH($E70),1),ROUND(N($J70)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B70",
            "'DATA CAPEX'!$I70",
            "'DATA CAPEX'!$E70",
            "'DATA CAPEX'!$J70"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P71": {
          "formula": "IF(OR($B71=\"\",$I71<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E71),N($E71)>0,ISNUMBER($J71),N($J71)>0,ABS(N($J71)*12-ROUND(N($J71)*12,0))<0.00000001),EDATE(DATE(YEAR($E71),MONTH($E71),1),ROUND(N($J71)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B71",
            "'DATA CAPEX'!$I71",
            "'DATA CAPEX'!$E71",
            "'DATA CAPEX'!$J71"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "P72": {
          "formula": "IF(OR($B72=\"\",$I72<>\"Crédit-bail\"),\"\",IFERROR(IF(AND(ISNUMBER($E72),N($E72)>0,ISNUMBER($J72),N($J72)>0,ABS(N($J72)*12-ROUND(N($J72)*12,0))<0.00000001),EDATE(DATE(YEAR($E72),MONTH($E72),1),ROUND(N($J72)*12,0))-1,\"\"),\"\"))",
          "references": [
            "'DATA CAPEX'!$B72",
            "'DATA CAPEX'!$I72",
            "'DATA CAPEX'!$E72",
            "'DATA CAPEX'!$J72"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "financement_dette_b3_b42": {
      "shape_sha256": "11be8b5933f0d4d38f8301c4adfbef19362d04b5fa1af71862fc3e9fb51abe0a",
      "source_label": "Nom du financement",
      "default_sources": {}
    },
    "financement_dette_c3_c42": {
      "shape_sha256": "24005fe08fcf7c3ecdb7ef8968ca2e4170d8663020fc1b4bdb80d92a1baa591e",
      "source_label": "Nominal euros",
      "default_sources": {}
    },
    "financement_dette_d3_d42": {
      "shape_sha256": "8cf3b4a67149754884184d834bb895d4769c75e90d52e6c47557aed1c13568cf",
      "source_label": "Taux annuel",
      "default_sources": {}
    },
    "financement_dette_e3_e42": {
      "shape_sha256": "e77cc108737077bc1ce3b7afd009b699e649c41be9df069043b99a03c948366e",
      "source_label": "Durée en années",
      "default_sources": {}
    },
    "financement_dette_f3_f42": {
      "shape_sha256": "b4df24dab44e2877e8423920677ef0247323314baa8a2b8f48006b1368685093",
      "source_label": "Mode de remboursement",
      "default_sources": {}
    },
    "financement_dette_h3_h42": {
      "shape_sha256": "b20242d96f4baa803131b3caea93a4dfaede4722e0328eb33f0ab9230e9a459d",
      "source_label": "Différé en années",
      "default_sources": {}
    },
    "financement_dette_i3_i42": {
      "shape_sha256": "e589fb06a0c103dc7665c18e03f8130dcf8ee99b8ba9abc17032c38c28e88317",
      "source_label": "Date de souscription / tirage",
      "default_sources": {}
    },
    "financement_dette_j3_j42": {
      "shape_sha256": "9ac10e48d1e3e052e65d4630916c936aad128c62548407a905e8ccfe92adacf0",
      "source_label": "Nature du financement",
      "default_sources": {}
    },
    "data_financement_b14_b413": {
      "shape_sha256": "149b40fca32804ef217eeab45fe7200eb2135c160f098e3c76e8ba5f53af9db1",
      "source_label": "Contrepartie / opération",
      "default_sources": {}
    },
    "data_financement_c14_c413": {
      "shape_sha256": "a4e066f445a25609fa10d07edf2d3e017ad01a59230de9c7bf29ef882c372660",
      "source_label": "Code catégorie de financement",
      "default_sources": {}
    },
    "data_financement_d14_d413": {
      "shape_sha256": "4a7e930e285b7e38eb9fb6a05c345d17d87df353b41725baf584f964e27c7452",
      "source_label": "Montant euros",
      "default_sources": {}
    },
    "data_financement_e14_e413": {
      "shape_sha256": "16949bf1b74e99ef0c9f6779ea60bded466d5377bc4b0df23a577019aca382c7",
      "source_label": "Date d’encaissement prévue",
      "default_sources": {}
    },
    "data_financement_f14_f413": {
      "shape_sha256": "4a29ea547ae484e64263659a63a0e5b65f1c0ef4f315554699f4432384ed0449",
      "source_label": "Pre-money euros de l’opération equity",
      "default_sources": {}
    },
    "data_financement_g14_g413": {
      "shape_sha256": "af9975b28fe99abd425ec1fd3ee6e32348ddf2ea1f810ebce9b9e0780609fa15",
      "source_label": "Part R&D de la subvention exploitation",
      "default_sources": {}
    },
    "data_financement_h14_h413": {
      "shape_sha256": "8c8b129e4aea1993c1a01f6671a4f0e406236ece004b94624f864865590df776",
      "source_label": "Instrument / commentaire",
      "default_sources": {}
    },
    "financement_e_s_j3_j17": {
      "shape_sha256": "331d18a025b933c1050dcb6a2055aa040cce94fba1a5a3c92dcaf9ae4d951649",
      "source_label": "Décalage en mois par catégorie",
      "default_sources": {
        "J3": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J4": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J5": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J6": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J7": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J8": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J9": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J10": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J11": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J12": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J13": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J14": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J15": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J16": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        },
        "J17": {
          "formula": "'Sensi TCA'!$C$14",
          "references": [
            "'Sensi TCA'!$C$14"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "subvention_invest_a3_a23": {
      "shape_sha256": "9834e439182d45ecc3ac3f85d9e42b13f645079d421a433cb30c9a9e08284c1a",
      "source_label": "Nom de la subvention",
      "default_sources": {}
    },
    "subvention_invest_b3_b23": {
      "shape_sha256": "fe2f1d27852a7ea350252bedb31cb130a95de6fb5ae1563e963f607ab9a3b544",
      "source_label": "Type documentaire",
      "default_sources": {}
    },
    "subvention_invest_c3_c23": {
      "shape_sha256": "26c130bbce83f54785fabf80c5e24444f9cda8a4def69937be5698101c793993",
      "source_label": "Assiette ou montant support euros",
      "default_sources": {}
    },
    "subvention_invest_d3_d23": {
      "shape_sha256": "5a664967ce6ebecfcd7a31ae9531750af234424f698213a27153bf092df471ac",
      "source_label": "Taux appliqué au montant support",
      "default_sources": {}
    },
    "subvention_invest_e3_e23": {
      "shape_sha256": "3e9ab3378e2db6ed045b8e40d850787786e62d6ff6083d2ec47c7daa2461372c",
      "source_label": "Durée de reprise en années",
      "default_sources": {}
    },
    "subvention_invest_f3_f23": {
      "shape_sha256": "b5cddb1c1f77a3f1ad94e7c8619be4edd0fde52bd4f19f98d3a8e604c1a9f63d",
      "source_label": "Mode documentaire (moteur linéaire)",
      "default_sources": {}
    },
    "subvention_invest_g3_g23": {
      "shape_sha256": "38a9125b0b41e4fd4dc4243d5276f32a1f9bb448ec2754b639be270513127dc4",
      "source_label": "Part acompte",
      "default_sources": {}
    },
    "subvention_invest_h3_h23": {
      "shape_sha256": "7990f68a8b7b01c4908784e1199526cf0ef31236fea639a5b01c1af10302275b",
      "source_label": "Date acompte",
      "default_sources": {}
    },
    "subvention_invest_i3_i23": {
      "shape_sha256": "afa60e851cde878a15f8b0adffee4e77ab550cf348027da3179101a3990ecd31",
      "source_label": "Part solde",
      "default_sources": {}
    },
    "subvention_invest_j3_j23": {
      "shape_sha256": "bdad4fa95d9c7842c9851b083fed330468df8635c8e32c69e39ba77cbff7710c",
      "source_label": "Date solde",
      "default_sources": {}
    },
    "subvention_invest_k3_k23": {
      "shape_sha256": "96afcf446bf592742b74d24c808c18fa1299dfdf78e75459577414e6e0943913",
      "source_label": "Date début reprise au résultat",
      "default_sources": {}
    },
    "subvention_invest_m3_m23": {
      "shape_sha256": "146b9bcddaec6117787f9798afccc2dea88dbc91d92553ddf8bfe8a38e66602d",
      "source_label": "Source / catégorie documentaire",
      "default_sources": {}
    },
    "calcul_cir_c18_m18": {
      "shape_sha256": "b749c9c9002a58f32202c2b93abaad92f2137affe0e28fa5b7ec6000f12078dd",
      "source_label": "Sous-traitance R&D documentée euros",
      "default_sources": {}
    },
    "calcul_cir_c19_m19": {
      "shape_sha256": "996488ee1f86302466d7b1696e05678b0056a3629334798a63b832334dec8028",
      "source_label": "Frais de normalisation euros",
      "default_sources": {}
    },
    "calcul_cir_c41_m41": {
      "shape_sha256": "6a1b0a736e7a63824131a56d3c04118fee3387b558d7646bad0179b1a21b9b65",
      "source_label": "Aides R&D supplémentaires à déduire euros",
      "default_sources": {}
    },
    "calcul_cir_c42_m42": {
      "shape_sha256": "42c68a414df7c241d0990ecc43042ca5a5bad473ab3193ce62e57920910a4e00",
      "source_label": "Remboursements d’aides à réintégrer euros",
      "default_sources": {}
    },
    "calcul_cir_c43_m43": {
      "shape_sha256": "ad30f83a2a2f672507aa5c0f6005080e0c113af0a88c632599f8946b14956e6d",
      "source_label": "Qualification des aides / affectation R&D",
      "default_sources": {}
    },
    "calcul_cir_c44_m44": {
      "shape_sha256": "1c3a909bcab1982f4ed8d04be4afc075e54f6780e7681cc4622e8457579b7e04",
      "source_label": "Sources et explication de la ventilation des aides",
      "default_sources": {}
    },
    "atelier_cir_is_c66_m66": {
      "shape_sha256": "5a6f80aa7bc80c597cc3d6e6f83ddf0e9e0698126f4dac9a301c7f4f235e8246",
      "source_label": "Conditions capital libéré / détention admissible",
      "default_sources": {}
    },
    "atelier_cir_is_c79_m79": {
      "shape_sha256": "6161d361df2323f5d41b1bebbef365e98e38e1def581462a79cc60667d27e350",
      "source_label": "Mois restitution trop-versés IS/contribution",
      "default_sources": {}
    },
    "atelier_cir_is_c85_m85": {
      "shape_sha256": "bd6a88f9715dc060c94ea00bed243b70edcfc18d265c7391acbc3fa0169efdf1",
      "source_label": "Exonération taxe additionnelle CVAE",
      "default_sources": {}
    },
    "atelier_cir_is_c89_m89": {
      "shape_sha256": "56be66b3e291f8f2875416e2e161b0d33f48555635006ac8390504bfe22099cb",
      "source_label": "Autres loyers corporels longs à réintégrer CVAE",
      "default_sources": {}
    },
    "atelier_cir_is_c91_m91": {
      "shape_sha256": "048d9cfb774c1233fd5c54a0f554d21937eab87e94e8297974c4fa231d6f7708",
      "source_label": "CFE selon avis annuel",
      "default_sources": {}
    },
    "atelier_cir_is_c110_m110": {
      "shape_sha256": "b3431a167de93c308108e0bce91687d27f777e80f8c8e4a8878935d318f7f53d",
      "source_label": "CA de groupe pour IS et contribution",
      "default_sources": {}
    },
    "atelier_cir_is_c111_m111": {
      "shape_sha256": "1d491144eb2b1dd25caf96feac7b56e808d6c93226ef54df396ca932e923e080",
      "source_label": "CA de groupe pour CVAE",
      "default_sources": {}
    },
    "atelier_cir_is_c93": {
      "shape_sha256": "0c686556217216eb6466cae7e4d62e1eeffe536fe3571a2a414d5afee7a53db8",
      "source_label": "CFE exercice précédant le plan",
      "default_sources": {}
    },
    "atelier_cir_is_c117_m117": {
      "shape_sha256": "65249503ebfb323b9cfcc1a56377bcbe09cb1a4570b21104eaf02977c2eb71bc",
      "source_label": "Commentaire sur l’antériorité fiscale",
      "default_sources": {}
    },
    "atelier_cir_is_d143_d155": {
      "shape_sha256": "c4e92a6520eaf335a2523b3e0dbd97b31c86d661667eb444c3457462532784e3",
      "source_label": "Régime TVA par offre",
      "default_sources": {}
    },
    "atelier_cir_is_e143_e155": {
      "shape_sha256": "bc45fc3532ff52cd5889623ff52b498ee93fb75ddab48fad5770b6f36d68c802",
      "source_label": "Taux TVA client par offre",
      "default_sources": {}
    },
    "atelier_cir_is_f143_f155": {
      "shape_sha256": "31d576187d66c81a8f726005dadff14da5155cd9d8e75d8601a81aefd979ee8f",
      "source_label": "Confirmation régime TVA par offre",
      "default_sources": {}
    },
    "atelier_cir_is_d160": {
      "shape_sha256": "824c55b8e97750e60e875af6b6fbad02a205eae14e9da46bdc3304dd20ad627d",
      "source_label": "Périodicité de déclaration implémentée",
      "default_sources": {}
    },
    "atelier_cir_is_d161": {
      "shape_sha256": "286fd777201b07e639b55b9be53b0132ce38a3dbd0e81dec09a05b69e5018a02",
      "source_label": "Délai paiement TVA mois",
      "default_sources": {}
    },
    "atelier_cir_is_d162": {
      "shape_sha256": "86d265f4093a6498565f90ad8e0c4963d9c6d3abcdbc951f1a2b46d2258edb04",
      "source_label": "Demande remboursement crédit TVA",
      "default_sources": {}
    },
    "atelier_cir_is_d163": {
      "shape_sha256": "eec372d501f9f679af7c144ef205132a8e490373e1261a375fab194fac9d241f",
      "source_label": "Délai encaissement remboursement mois",
      "default_sources": {}
    },
    "atelier_cir_is_d164": {
      "shape_sha256": "1c3a3eaf046ae7a1de1aca2012c71a8eaf59becf735410f75a22e2918e9e88e2",
      "source_label": "Seuil demande mensuelle euros",
      "default_sources": {}
    },
    "atelier_cir_is_d165": {
      "shape_sha256": "a56e8ca3a871866bf3e7d34b65cd9b9ac81be433f7892ede1784a1661dac9019",
      "source_label": "Seuil demande décembre euros",
      "default_sources": {}
    },
    "atelier_cir_is_d166": {
      "shape_sha256": "703c54c0ebcb5534f4d5f8826539d110f75ea560952267dfc8b1ab290e12760e",
      "source_label": "Confirmation paramètres TVA",
      "default_sources": {}
    },
    "assumptions_d68": {
      "shape_sha256": "d4cab7e3e006c0472cfe07c64b9603cef4a74ddfd8de2595103442fc67d3c171",
      "source_label": "CIR : taux - part <= 100 M EUR",
      "default_sources": {}
    },
    "assumptions_d69": {
      "shape_sha256": "3eddc8cef5e508d8e854eca8bd2035a558f25d0b3c7c5064837617b91c487503",
      "source_label": "CIR : taux - part > 100 M EUR",
      "default_sources": {}
    },
    "assumptions_d70": {
      "shape_sha256": "bc40365f16fc59e8d854d587af151131db82bff02fc85b42f2ed7679b8f66cd3",
      "source_label": "CIR : forfait fonctionnement, % des depenses de personnel",
      "default_sources": {}
    },
    "assumptions_d71": {
      "shape_sha256": "1de01ce28c9cfc4a38d1d22bd76b671ed2602a409edfaf6b94374695113f2df8",
      "source_label": "CIR : forfait fonctionnement, % des amortissements",
      "default_sources": {}
    },
    "assumptions_d72": {
      "shape_sha256": "4df57fb2ec95e7c1d25b5a9e635637b6e4867b09970dcdb96db12805acbf789f",
      "source_label": "CIR : sous-traitance, plafond en multiple des autres depenses",
      "default_sources": {}
    },
    "assumptions_d73": {
      "shape_sha256": "6328d399e786c31ab5c21a1db464da6b147dd01a4e6c2c5f3b62e55393219cfe",
      "source_label": "CIR : sous-traitance, plafond global",
      "default_sources": {}
    },
    "assumptions_d74": {
      "shape_sha256": "0ebda767aba32c8b8b7b4873c04167448da26dcf1c9758d28655b8ae64462655",
      "source_label": "CIR : frais de normalisation, part eligible",
      "default_sources": {}
    },
    "assumptions_d75": {
      "shape_sha256": "f71bac14173716d7ee12b6a2e3391f2187b5594b60dce552391b36290d46b240",
      "source_label": "CIR : delai de remboursement",
      "default_sources": {}
    },
    "assumptions_d76": {
      "shape_sha256": "bb31e8e2e0fcebd921f439866b582d0625eb333a384851b61e5869c60d665f7e",
      "source_label": "CIR : mois d encaissement du remboursement",
      "default_sources": {}
    },
    "assumptions_d77": {
      "shape_sha256": "ca3f7705b5d56dbfe1db60bf9adf2a78aa3efe33eec89d39512e89f36b951dcd",
      "source_label": "IS : seuil du taux reduit PME",
      "default_sources": {}
    },
    "assumptions_d78": {
      "shape_sha256": "4a20ec8da492428f97717b028ff3d87d10e4f8696d2e91069945c2a7e3d0296a",
      "source_label": "IS : taux reduit sous le seuil",
      "default_sources": {}
    },
    "assumptions_d79": {
      "shape_sha256": "bcaf52740381a6eb12aa442a5fd4c2ecb6f6d1b848321644a52a894e7aa1a737",
      "source_label": "IS : taux normal",
      "default_sources": {}
    },
    "assumptions_d83": {
      "shape_sha256": "7a7ffa86f343c1de798e1c43ab83c70ee241f51b11713ce8027e7e6135aa620a",
      "source_label": "Taux TVA achats/fournisseurs (libellé historique ventes/achats trop large)",
      "default_sources": {}
    },
    "assumptions_d84": {
      "shape_sha256": "56a595681b7c43b2cf88a53326ecbe768499415a46f124020e71123440cede78",
      "source_label": "C3S : abattement d assiette",
      "default_sources": {}
    },
    "assumptions_d85": {
      "shape_sha256": "a545026917f2a5fb605c5160e15629b811c6c79d627fa29182821bdc63f934b1",
      "source_label": "C3S : taux",
      "default_sources": {}
    },
    "assumptions_d86": {
      "shape_sha256": "421a8f384391da4791076bb67faaccc944d323dd9af2567163a3c14d4a896c1f",
      "source_label": "CFE : cotisation minimum annuelle",
      "default_sources": {}
    },
    "assumptions_d87": {
      "shape_sha256": "522d77edc09a395aa0cabe4d59a4d04a3cbcb586c30ff1946eb90a957349b5c3",
      "source_label": "CFE : taux communal applique a la valeur locative",
      "default_sources": {}
    },
    "assumptions_d88": {
      "shape_sha256": "1b6e4b29745a4361170c8597d5578333a17f0a05074528a7cbb15a41be61459f",
      "source_label": "CVAE : seuil de CA déclenchant une cotisation (distinct du seuil déclaratif)",
      "default_sources": {}
    },
    "assumptions_d91": {
      "shape_sha256": "5e4491c90670a030b00fa504d9e0a53a21d933a9a50cb5b27325f3c71ecfe07c",
      "source_label": "Taux annuel de crédit-bail par défaut",
      "default_sources": {}
    },
    "assumptions_d93": {
      "shape_sha256": "05a2c212d41628638a58a0c86f01657bd41511f2433752054e2e2614105506dd",
      "source_label": "Part R&D de la subvention d'investissement (déduction CIR via la reprise)",
      "default_sources": {}
    },
    "valorisation_d8": {
      "shape_sha256": "10225fdb56c29af78ead14e342fff86fe379cd6e5684c71f8e1143580503e7df",
      "source_label": "Croissance terminale g",
      "default_sources": {}
    },
    "valorisation_d9": {
      "shape_sha256": "fe00b42eb6352fb0ab3b8aa2b6c613c59e66e69f103a1c940fb355233f31ac81",
      "source_label": "IS normatif DCF",
      "default_sources": {}
    },
    "valorisation_d12": {
      "shape_sha256": "3cd26a40953c1df90031f60e4056674fe202ff88a237f41f616284860926227f",
      "source_label": "Poids EBE dans le mix EBE/CA",
      "default_sources": {}
    },
    "valorisation_d13": {
      "shape_sha256": "62bb46f0396973a98e428adf6d352e7fa2f8df5cef8fdecfc9976a5e044c44e0",
      "source_label": "Taux actualisation VC",
      "default_sources": {}
    },
    "valorisation_d57": {
      "shape_sha256": "0e53fd0c6881b4eadacd2f30a2d2cd8be894645e398ef0bd08dda1fc4a6f116a",
      "source_label": "Pre-money proposé pour négociation euros",
      "default_sources": {}
    },
    "valorisation_d107": {
      "shape_sha256": "5b08e8908ae08f742dfc3d254efc8e1366720b4ce45bb21e26c3a307de73523b",
      "source_label": "Mode WACC",
      "default_sources": {}
    },
    "valorisation_d108": {
      "shape_sha256": "49a1de98868a0ee8a44ac4ea1fabc34d3e20ce326c9219a4ceaf3c752d7b9d82",
      "source_label": "WACC manuel",
      "default_sources": {}
    },
    "valorisation_d111": {
      "shape_sha256": "097f1c0abbeccc9eac44791c767310ef650322933df0f2edbec0ec1045287f12",
      "source_label": "Date de référence des données de marché",
      "default_sources": {}
    },
    "valorisation_d113": {
      "shape_sha256": "f987f2a14d153cd8e87e26e720f11932fdbe9ceb8c7a57ca6990bd5dbe74023f",
      "source_label": "Prime de risque actions",
      "default_sources": {}
    },
    "valorisation_d116": {
      "shape_sha256": "968a56ad31e5773447535c30fb969cf1bf3d64f31e343877c8527ceca9435412",
      "source_label": "Coût de la dette avant IS",
      "default_sources": {}
    },
    "valorisation_d117": {
      "shape_sha256": "67339479194513368041bfc41b1fb518b40abd36e523d92b32116e446ec19f6b",
      "source_label": "Prime de taille",
      "default_sources": {}
    },
    "valorisation_d118": {
      "shape_sha256": "6ba40337f999de7bc4b599575a364488b54df45110f2d931d18869c7ed682f5b",
      "source_label": "Prime spécifique exécution",
      "default_sources": {}
    },
    "valorisation_d119": {
      "shape_sha256": "a6e18641fd6cee3001809aee9efecc6f6f056e09ecb8bfb97bf496fe3e80065d",
      "source_label": "Prime illiquidité",
      "default_sources": {}
    },
    "valorisation_d120": {
      "shape_sha256": "b7a79fd71bab9787010efb60d3719111ecb75c27537ae18dfaeb6a835f7bc0f3",
      "source_label": "Traitement risque exécution",
      "default_sources": {}
    },
    "valorisation_d121": {
      "shape_sha256": "0626cdb3efbdd01bca0acce533a3f96dd89ff20c4b510bde63f4d910961cb7d9",
      "source_label": "Flux déjà abattus pour même risque",
      "default_sources": {}
    },
    "valorisation_d122": {
      "shape_sha256": "dd7a912f5aba81d0236ee2440997a508ad88305542076b5fe02ffe370a026fbb",
      "source_label": "Décote taille appliquée aux multiples",
      "default_sources": {}
    },
    "valorisation_d123": {
      "shape_sha256": "497e8dff52b4583b3d590420c4068ab4f6ac2ca74c8c63ae1a9de7ac11435d26",
      "source_label": "DLOM appliquée à cette même valeur",
      "default_sources": {}
    },
    "valorisation_d124": {
      "shape_sha256": "47c8590a183d78e4e92d4aee895ffb1751b02658dfbd9869b44134a844740693",
      "source_label": "Levier cible dette brute / equity",
      "default_sources": {}
    },
    "valorisation_d161": {
      "shape_sha256": "e4556bd167ff05c9938a46559234d02ce91387d16982a3765b1da9d1fd3f455a",
      "source_label": "Cible indicative de pre-money euros",
      "default_sources": {}
    },
    "valorisation_d16": {
      "shape_sha256": "b1b7552b78936b5dd388f79afd2708d01b6b7d6e1a6d19082e71c52aac3950c9",
      "source_label": "Année de sortie VC",
      "default_sources": {
        "D16": {
          "formula": "Control!$C$60",
          "references": [
            "'Control'!$C$60"
          ],
          "dynamic_or_named_references_require_review": false
        }
      }
    },
    "valorisation_d112": {
      "shape_sha256": "48ee94d9ce4845fd659824366c384beefb67219695349e2fc8b6c76758c1b693",
      "source_label": "Taux sans risque justifié",
      "default_sources": {}
    },
    "valorisation_e112": {
      "shape_sha256": "44294fedf7efb136e6ef0fc6a8e4a86ede6cb35b24d8f886cd6d4ac7c189690d",
      "source_label": "Source / justification 112",
      "default_sources": {}
    },
    "valorisation_e113": {
      "shape_sha256": "ab0f04899a11331b457c62bdbffd49f71c7b27e7cd08bce422b27b7ea4e40887",
      "source_label": "Source / justification 113",
      "default_sources": {}
    },
    "valorisation_e116": {
      "shape_sha256": "6acaaa6c3d620023b4ee2714c799eb99ceeb47c5d595b62c80ecac5dac1e1540",
      "source_label": "Source / justification 116",
      "default_sources": {}
    },
    "valorisation_e117": {
      "shape_sha256": "829b9185a8c5d9c03ed72fc439e722b84d33697dd84b55b4cde746c4a8f44c0f",
      "source_label": "Source / justification 117",
      "default_sources": {}
    },
    "valorisation_e118": {
      "shape_sha256": "cc116d90723cdaf623958cb001856ebc4b9f2a356a8c266c73ebc2de74fc82a6",
      "source_label": "Source / justification 118",
      "default_sources": {}
    },
    "valorisation_e119": {
      "shape_sha256": "c8f630a5333f52e84836a68f9c8e3255b29087a6dd3bcaaaa3843869b5bf0ff8",
      "source_label": "Source / justification 119",
      "default_sources": {}
    },
    "valorisation_e125": {
      "shape_sha256": "356af241acb06f8df84acaa9df080e3df0fd5f9a0e0910e208f9454b0acfe0c4",
      "source_label": "Source / justification 125",
      "default_sources": {}
    },
    "comparables_h9": {
      "shape_sha256": "bf26e6f24c587da6381a5e312a9c9036825fd5c7cd5ae8ce1787920869457675",
      "source_label": "Marge EBITDA minimale admissible",
      "default_sources": {}
    },
    "comparables_h10": {
      "shape_sha256": "22dc5990f80d101dbecdcc13579c6411e918f098883ccbd0c2a3709ec06e2537",
      "source_label": "Plafond multiple EV/EBITDA",
      "default_sources": {}
    },
    "comparables_s14_ad16": {
      "shape_sha256": "06e9b7831fb3c313ae793309ea1fa875af04aa50fbb649c50b791d92a36eb96c",
      "source_label": "Poids des statistiques par source CA/EBITDA",
      "default_sources": {}
    },
    "comparables_b25_b32": {
      "shape_sha256": "4496955f1dee14f875c04ec5aa939b723085111e8d787227d9f8f9e11ca27bdb",
      "source_label": "Libellé indice",
      "default_sources": {}
    },
    "comparables_c25_c32": {
      "shape_sha256": "04e565eacaefa6b3c4e17af562f94709f5f8dd8347bc32b9225cc3ef4f72567e",
      "source_label": "Multiple EV/CA",
      "default_sources": {}
    },
    "comparables_d25_d32": {
      "shape_sha256": "0f879bcd946c02e04c25ee0d742a1687566d1a5e6e65e8cdc766682e40567f6c",
      "source_label": "Multiple EV/EBITDA",
      "default_sources": {}
    },
    "comparables_e25_e32": {
      "shape_sha256": "0306c1d38ab0935ede332c71f0446fb5d7ae1c0c3ac248eff9d7c3d9e90e20da",
      "source_label": "Score pertinence CA",
      "default_sources": {}
    },
    "comparables_f25_f32": {
      "shape_sha256": "68e15e80930dd6cd747a4ce23d140a18d28686548d2eb516ec6311d4f1b2e942",
      "source_label": "Score pertinence EBITDA",
      "default_sources": {}
    },
    "comparables_i25_i32": {
      "shape_sha256": "0b3e94d4578d0d1a0022b8be57f1501b29287a323fada7686be9af6a66672dc1",
      "source_label": "Source indice",
      "default_sources": {}
    },
    "comparables_j25_j32": {
      "shape_sha256": "c56e11248201332147ef516ed4c136d17de9042bf9e7b4d023dcd8f3e8571b29",
      "source_label": "Hypothèses indice",
      "default_sources": {}
    },
    "comparables_b47_b61": {
      "shape_sha256": "04947812f597c92d25dd9721b1f26d79bfd27b02933417bb60615b9c33b296a8",
      "source_label": "société : Société / acquéreur",
      "default_sources": {}
    },
    "comparables_c47_c61": {
      "shape_sha256": "475a44b07d51e7a2e39c2cd082c59d87b1360c045c2f06155c2f7cf89e1834e6",
      "source_label": "société : Pays / cible",
      "default_sources": {}
    },
    "comparables_d47_d61": {
      "shape_sha256": "55df69ae13a2d815601ab4fd67c3647d978f8d7b076846e0eb3bd1f73f88829c",
      "source_label": "société : Statut / activité de la cible",
      "default_sources": {}
    },
    "comparables_e47_e61": {
      "shape_sha256": "2bf0eafef89426996d284b98debf182b21a7a4e091109249e51a8c46a4611316",
      "source_label": "société : CA en M EUR",
      "default_sources": {}
    },
    "comparables_f47_f61": {
      "shape_sha256": "199075bcc718f7f74f22cde5c6de876376eb3b27c003b230833ea0fec2829406",
      "source_label": "société : EBITDA en M EUR",
      "default_sources": {}
    },
    "comparables_g47_g61": {
      "shape_sha256": "fa576b00504b2c91a7b8ed0a85401363052948b4fc0be03f8e2e9bb80c0e0079",
      "source_label": "société : Valeur entreprise en M EUR",
      "default_sources": {}
    },
    "comparables_j47_j61": {
      "shape_sha256": "11836244833d2a5a76b0c1d691ebf8379325115bc6b59128d20514d769351ac9",
      "source_label": "société : Score pertinence CA",
      "default_sources": {}
    },
    "comparables_k47_k61": {
      "shape_sha256": "5648acf257d946534c02552ae62f218758eac22786975782324bbed9164572ae",
      "source_label": "société : Score pertinence EBITDA",
      "default_sources": {}
    },
    "comparables_n47_n61": {
      "shape_sha256": "787ff2881832722be66b1cda6ec55c7627847d7abc28ff814cbdf36aeb93bb24",
      "source_label": "société : Sources, date, périmètre et hypothèses",
      "default_sources": {}
    },
    "comparables_b76_b103": {
      "shape_sha256": "96f1b213a6bb2a134abc6b6a4af44757a311b265c694867cb963efd913ce0fd2",
      "source_label": "transaction : Société / acquéreur",
      "default_sources": {}
    },
    "comparables_c76_c103": {
      "shape_sha256": "3fa3db700a3fe04884ac4b0a907174b25df340041450a65259347ef75263261d",
      "source_label": "transaction : Pays / cible",
      "default_sources": {}
    },
    "comparables_d76_d103": {
      "shape_sha256": "3e217ec541ad909dc4ef6145dd977ef96a2d8fe7fcd73f59328d560133939aa9",
      "source_label": "transaction : Statut / activité de la cible",
      "default_sources": {}
    },
    "comparables_e76_e103": {
      "shape_sha256": "793ab8a81699debc3fc48884532b3e4aa00d2d570ebc083e246f2ebaba3411af",
      "source_label": "transaction : CA en M EUR",
      "default_sources": {}
    },
    "comparables_f76_f103": {
      "shape_sha256": "91ec8bb2a1203e3b6e8751af13af751e4add634ff21b4f27dd91281343cc854d",
      "source_label": "transaction : EBITDA en M EUR",
      "default_sources": {}
    },
    "comparables_g76_g103": {
      "shape_sha256": "6442ab57b539577946112917bf2f47ae3cb0393d5b01b5a24b743bd645bf8a41",
      "source_label": "transaction : Valeur entreprise en M EUR",
      "default_sources": {}
    },
    "comparables_j76_j103": {
      "shape_sha256": "9a5d449a1f26128d8dc6d50059f97ca1149df80157e396024a95e1d2af470d5b",
      "source_label": "transaction : Score pertinence CA",
      "default_sources": {}
    },
    "comparables_k76_k103": {
      "shape_sha256": "4eec8d119607f15383f98eab85709bb56afc8f07b69df60b75b104cd4c54c5bc",
      "source_label": "transaction : Score pertinence EBITDA",
      "default_sources": {}
    },
    "comparables_n76_n103": {
      "shape_sha256": "cdb640c65bccec2afca2f03fdcac386763d12a3dab8ba533f79c98aa2d0e95c7",
      "source_label": "transaction : Sources, date, périmètre et hypothèses",
      "default_sources": {}
    },
    "comparables_b117_b136": {
      "shape_sha256": "145ea2f79b910a7573907ba821c72db6b72ad06c47c1af997d1a73dca3a7e1f5",
      "source_label": "Identifiant société cotée",
      "default_sources": {}
    },
    "comparables_c117_c136": {
      "shape_sha256": "00fec6cc8a72c8a861646e8f22d3986df3ff04978910c903f5d0579c55cc0af2",
      "source_label": "Inclure dans médiane bêta",
      "default_sources": {}
    },
    "comparables_d117_d136": {
      "shape_sha256": "1f7395015ca8fae544a429f70d7c475e18bc6023d8e7090c1aa3c94c252243dd",
      "source_label": "Bêta endetté",
      "default_sources": {}
    },
    "comparables_e117_e136": {
      "shape_sha256": "d4ab4c907ba007963f0dd258ef1b878d8c8188249f1a540f4aed6f6182e5e8fd",
      "source_label": "Equity de marché",
      "default_sources": {}
    },
    "comparables_f117_f136": {
      "shape_sha256": "28fbe2cc0e183d394a2abe8e410cfc3885fa4c4fae9eb23a016f6f57e8b08083",
      "source_label": "Dette financière brute",
      "default_sources": {}
    },
    "comparables_g117_g136": {
      "shape_sha256": "988fceb41b19380df0d906169fd262164d1a89b9975833f29e7e4e72720fb6ce",
      "source_label": "Taux marginal IS",
      "default_sources": {}
    },
    "comparables_j117_j136": {
      "shape_sha256": "d0dc65796e2f1a3e07c6f2f668eec96f8432baf9961208be9c2e4ab39aaf483a",
      "source_label": "Date des données",
      "default_sources": {}
    },
    "comparables_k117_k136": {
      "shape_sha256": "95743aa9f59e3c04232a8866dd80df2944ae78e32089f300e274ef3719f0dad5",
      "source_label": "Sources et périmètre dette",
      "default_sources": {}
    },
    "comparables_l117_l136": {
      "shape_sha256": "94010fbd956f530e71249eb70e0dd5b676649c7f0695385542ae91d25c438749",
      "source_label": "Fréquence du bêta",
      "default_sources": {}
    },
    "comparables_m117_m136": {
      "shape_sha256": "a12e3332846a34afe7a980b00138f1aff735f898a77a1d86b952622123012da4",
      "source_label": "Fenêtre du bêta en années",
      "default_sources": {}
    },
    "model_start_date": {
      "shape_sha256": "ccc3b5b8058dc1ab10334997dbe3aa77483974660c433370ddc428ab049f1412",
      "source_label": "Date de début du modèle",
      "default_sources": {}
    },
    "capex_catalog_years": {
      "shape_sha256": "3fad2e1122e2fb0e218dd1ef3965585447b39b7f90a67cc7367738ea65ca6041",
      "source_label": "Durées proposées par le catalogue CAPEX",
      "default_sources": {}
    },
    "capex_catalog_rd_share": {
      "shape_sha256": "57cb12274cc5237ad2f710521336e91ba7609e9512768a526b66d622cf0d88f5",
      "source_label": "Quote-part R&D proposée par le catalogue CAPEX",
      "default_sources": {}
    },
    "financing_rd_default": {
      "shape_sha256": "8a75bcef2d3bc613aed7765cf7663589590104a6d50361cc3cd6f65adecce675",
      "source_label": "Quote-part R&D par catégorie de financement",
      "default_sources": {}
    }
  },
  "witnesses": {
    "Assumptions!AA15": {
      "formula": "V15+X15+Z15-1",
      "value": null
    },
    "Assumptions!G15": {
      "formula": "F15*(1+$D$5)",
      "value": null
    },
    "Assumptions!W14": {
      "formula": null,
      "value": "Acompte : avance (mois)"
    },
    "Assumptions!Y14": {
      "formula": null,
      "value": "Jalon : avance (mois)"
    },
    "COGS!P38": {
      "formula": "P30+(Contrats!P221+(P28-Contrats!P221)*Control!$C$22)*(INDEX($E31:$N31,1,MATCH(P$5,$E$5:$N$5,0))+INDEX($E32:$N32,1,MATCH(P$5,$E$5:$N$5,0))+INDEX($E33:$N33,1,MATCH(P$5,$E$5:$N$5,0)))+P29*(INDEX($E34:$N34,1,MATCH(P$5,$E$5:$N$5,0))+INDEX($E35:$N35,1,MATCH(P$5,$E$5:$N$5,0)))",
      "value": null
    },
    "Charges_Externes!E15": {
      "formula": "($E32+$F32*E$10+$G32*E$12)*(1+$I32)^(E$5-$E$5)+$H32*IF($J32=\"CA reconnu\",E$13,E$11)+$K32*E$47+$L32*E$48",
      "value": null
    },
    "Charges_Externes!F31": {
      "formula": null,
      "value": "EUR / ETP"
    },
    "Charges_Externes!G31": {
      "formula": null,
      "value": "EUR / unite produite"
    },
    "Charges_Externes!K31": {
      "formula": null,
      "value": "% des immobilisations brutes"
    },
    "Comparables!I117": {
      "formula": "IF(N117=\"OK\",D117/(1+(1-G117)*H117),\"\")",
      "value": null
    },
    "DATA COGS!I15": {
      "formula": "$E15+$F15+$G15+$H15",
      "value": null
    },
    "DATA COGS!J14": {
      "formula": null,
      "value": "% du CA"
    },
    "DATA COGS!K14": {
      "formula": null,
      "value": "% du CA"
    },
    "DATA Contrats!G14": {
      "formula": "IF($B14=\"\",\"\",N($E14)*N($F14))",
      "value": null
    },
    "DATA Contrats!X14": {
      "formula": "IF($B14=\"\",0,N($G14)*IF(OR($R14=\"Signe\",$R14=\"Signé\"),1,IF($S14=\"\",1,N($S14))))",
      "value": null
    },
    "Sensi Analyses!E13": {
      "formula": "(1+C13)*(1+D13)-1",
      "value": null
    },
    "Stock!C10": {
      "formula": null,
      "value": "jours"
    },
    "Stock!C11": {
      "formula": null,
      "value": "jours"
    },
    "Stock!Q15": {
      "formula": "MAX(Q14*$E$10/30,Control!$C$31-Q14)",
      "value": null
    },
    "Stock!Q19": {
      "formula": "IF(Q$6-ROUND($E$11/30,0)<1,0,INDEX($Q$18:$EF$18,1,Q$6-ROUND($E$11/30,0)))+IFERROR(IF(AND(ISNUMBER(Control!$C$55),YEAR(Control!$C$55)*100+MONTH(Control!$C$55)=Q$3),Control!$C$32,0),0)",
      "value": null
    }
  },
  "limits": [
    "Semantic contract, not confirmation of a client value or statutory rule.",
    "Formula witnesses concern dimensions and bases; local calendar rewrites outside witnesses do not invalidate the catalogue.",
    "Dynamic references require explicit review; the extracted dependency graph remains a separate sealed artifact."
  ]
}''')
