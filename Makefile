docker-push:
	docker run -d --name serving-push tfserving
	docker commit serving-push quay.io/addapptech/tfserving
	docker push quay.io/addapptech/tfserving
	docker rm serving-push

help:
	@echo '    docker-push'
	@echo '        Destroy the docker containers already running, build and run the services `data-science-api`.'