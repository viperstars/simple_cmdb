# -*- coding:utf8 -*-

from app.models import ManagementCard, db
from app.utils import check_params, check_output


def create(**kwargs):

    check_params(ManagementCard, kwargs)

    management = ManagementCard(**kwargs)

    try:
        db.session.add(management)
        db.session.commit()
    except Exception, e:
        print e
        db.session.rollback()
        pass

    if management.id:
        return management.id
    else:
        return 0


def get(**kwargs):
    output = kwargs.get("output", None) or []
    limit = kwargs.get("limit", None) or 20
    order = kwargs.get('order', None) or "id desc"
    where = kwargs.get("where", None)

    check_output(output, ManagementCard)

    order_by = ("desc", "asc")
    order_list = order.split()

    if not hasattr(ManagementCard, order_list[0]):
        raise Exception("{0} is not a valid attribute".format(order_list[0]))
    if order_list[1] not in order_by:
        raise Exception("{0} is not a valid value".format(order_list[1]))

    if not isinstance(limit, int):
        raise Exception("{0} is not a valid value".format(limit))

    order_obj = getattr(getattr(ManagementCard, order_list[0]), order_list[1])


    if where:
        management_list = db.session.query(ManagementCard).filter_by(**where).order_by(order_obj()).limit(limit).all()
    else:
        management_list = db.session.query(ManagementCard).order_by(order_obj()).limit(limit).all()


    def output_func(obj, output):
        attrs = dict()
        for x, y in obj.__dict__.iteritems():
            if x in output:
                attrs[x]=y
        return attrs

    def general_output(obj):
        obj.__dict__.pop('_sa_instance_state')
        return obj.__dict__

    if output:
        return [output_func(x, output) for x in management_list]
    else:
        return [general_output(x) for x in management_list]


def update(**kwargs):
    where = kwargs.get("where", None) or {}
    data = kwargs.get("data", None) or {}
    if not ("id" in where and where.get("id", None)):
        raise Exception("id not included")

    for x, y in data.iteritems():
        if not (hasattr(ManagementCard, x) and y):
            raise Exception("data wrong")
    management = db.session.query(ManagementCard).filter_by(**where).update(data)

    try:
        db.session.commit()
    except Exception as e:
        print e

    return management


def delete(**kwargs):
    where = kwargs.get("where", None) or {}
    if not("id" in where and where.get("id", None)):
        raise Exception("id not included")
    management = db.session.query(ManagementCard).filter_by(**where).all()

    if management:
        try:
            db.session.delete(management[0])
            db.session.commit()
        except Exception as e:
            print e
    else:
        raise Exception("id not in db")

    id = management[0].id
    management = db.session.query(ManagementCard).filter_by(id=id).all()
    if management:
        return id
