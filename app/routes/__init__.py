def register_routes(app):
    """Register all route blueprints with the Flask app.

    Add your blueprints here. Example:
        from app.routes.products import products_bp
        app.register_blueprint(products_bp)
    """
    from app.routes.shorten import shorten_bp
    from app.routes.redirect import redirect_bp
    app.register_blueprint(shorten_bp)
    app.register_blueprint(redirect_bp)
