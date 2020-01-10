.default: run

build-frontend:
	docker-compose -f ../docker-compose.yml -f docker-compose.yml build frontend

update:
	npm run build && docker-compose -f ../docker-compose.yml -f docker-compose.yml restart frontend

run:
	docker-compose -f ../docker-compose.yml -f docker-compose.yml up -d frontend

stop:
	docker-compose -f ../docker-compose.yml -f docker-compose.yml stop

version:
	$(eval GIT_TAG ?= $(shell git describe --abbrev=0))
	$(eval VERSION ?= $(shell read -p "Version: " VERSION; echo $$VERSION))
	echo "Tagged release $(VERSION)\n" > Changelog-$(VERSION).txt
	git log --oneline --no-decorate --no-merges $(GIT_TAG)..HEAD >> Changelog-$(VERSION).txt
	git tag -a -e -F Changelog-$(VERSION).txt $(VERSION)
