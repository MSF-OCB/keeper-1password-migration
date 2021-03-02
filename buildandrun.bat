@docker build . -t rest_endpoints
@docker run -p 8181:8181 --name rest_endpoints rest_endpoints
