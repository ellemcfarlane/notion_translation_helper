DEV_DB := "dev"
PROD_DB := "prod"
SPANISH := "es"
GERMAN := "de"

# TODO provide default value when arg not given
insert:
	python3 translation_importer.py -db $(DB) -l $(LANG) -s $(SEC) --max $(MAX)

es_prod: DB=$(PROD_DB)
es_prod: LANG=$(SPANISH)
es_prod: insert

es_dev: DB=$(DEV_DB)
es_dev: LANG=$(SPANISH)
es_dev: insert

de_prod: DB=$(PROD_DB)
de_prod: LANG=$(GERMAN)
de_prod: insert

de_dev: DB=$(DEV_DB)
de_dev: LANG=$(GERMAN)
de_dev: insert
