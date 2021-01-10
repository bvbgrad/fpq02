from app import create_app, db
import app.utils6L.utils6L as utils
from app.models import User

if __name__ == "__main__":
    utils.setup_logging()
    app = create_app()
    app.config.update (
        EXPLAIN_TEMPLATE_LOADING = False
    )
    app.run(host="0.0.0.0", port=8082)

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}
    