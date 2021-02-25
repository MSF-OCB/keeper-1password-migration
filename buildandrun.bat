@docker build . -t rest_endpoints
@docker run -p 8080:8080 --name rest_endpoints rest_endpoints
