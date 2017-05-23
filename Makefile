docker-push:
	docker build -t tfserving .
	docker run -d --name serving-push tfserving
	docker login -e="." -u="addapptech+team" -p="TUXC2USLHSVVTAYOJHU3IJI6B09S68IQ12X8NP71PXFLF1OMCSZP5LYWH014TCIU" quay.io
	docker tag tfserving quay.io/addapptech/tfserving:1.0
	docker commit serving-push quay.io/addapptech/tfserving
	docker push quay.io/addapptech/tfserving:1.0
	docker push quay.io/addapptech/tfserving
	docker rm serving-push

help:
	@echo '    docker-push'
	@echo '        Destroy the docker containers already running, build and run the services `data-science-api`.'