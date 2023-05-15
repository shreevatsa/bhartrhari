all: web/K001.html

data.json: data/alignment/*.csv gen/data.py gen/book.html gen/common.css
	python3 gen/data.py

web/K001.html: data.json gen/gen.py gen/template.html
	python3 gen/gen.py
