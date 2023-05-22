all: web/K001.html

data.db: data/alignment/*.csv gen/data.py gen/book.html web/common.css
	rm data.db
	python3 gen/data.py

web/K001.html: data.db gen/gen.py gen/template.html gen/morsel.html
	python3 gen/gen.py
