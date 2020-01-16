.default: update-frontend


update-frontend:
	cd frontend && npm run build && cd .. && docker-compose restart frontend

