from aiohttp.abc import AbstractAccessLogger

LOG_EXCLUDED = {
    "/api/log"
}


class AccessLogger(AbstractAccessLogger):

    def log(self, request, response, time):
        remote = request.headers.get('X-Forwarded-For', request.remote)
        refer = request.headers.get('Referer', '-')
        user_agent = request.headers.get('User-Agent', '-')
        if request.path not in LOG_EXCLUDED:
            self.logger.info(f'{remote} '
                             f'"{request.method} {request.path} {response.status}'
                             f'{response.body_length} {refer} {user_agent} '
                             f'{time:.6f}s"')
