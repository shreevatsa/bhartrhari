all: web/K001.html

data.db: data/alignment/*.csv gen/data.py
	rm -f data.db
	python3 gen/data.py

web/K001.html: data.db gen/gen.py gen/book.html gen/knum.html gen/morsel.html web/common.css
	python3 gen/gen.py
