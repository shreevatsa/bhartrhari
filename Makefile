all: web/K001.html

data.db: data/alignment/*.csv data/chaya/*.json gen/data.py gen/chaya.py
	rm -f data.db
	python3 gen/data.py

web/K001.html: data.db gen/gen.py gen/book.html gen/knum.html gen/morsel.html gen/index.html web/common.css web/common.js
	python3 gen/gen.py
