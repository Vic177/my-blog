from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors

from ..models import Permission, Category, Tag


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.app_context_processor
def inject_category():
	return dict(categories=Category.query.all())

@main.app_context_processor
def inject_tag():
	return dict(tags=Tag.query.all())
