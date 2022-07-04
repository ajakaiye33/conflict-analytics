install:
	#install commands
	pip install --upgrade pip &&\
		pip install -r requirement.txt

format:
	#format code
	black *.py data_prep/*.py
lint:
	pylint --disable=R,C,broad-except *.py data_prep/*.py
test:
	#test
build:
	#build container
	docker build -t data_prep:latest .
run:
	#run container
	docker run -p 8501:8501 data_prep:latest
deploy:
	#deploy
all:install format lint build run


