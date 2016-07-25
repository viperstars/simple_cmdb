# -*- coding:utf8 -*-

from app.models import Manufacturers, db
from app.utils import check_params


def create(**kwargs):

    check_params(Manufacturers, kwargs)


    man = Manufacturers(**kwargs)

    try:
        db.session.add(man)
        db.session.commit()
    except Exception, e:
        print e
        db.session.rollback()
        pass

    if man.id:
        return man.id
    else:
        return 0


def get(**kwargs):
    output = kwargs.get("output", [])
    limit = kwargs.get("limit", 20) or 20
    order = kwargs.get('order', "id desc")
    where = kwargs.get("where", {})

    if not isinstance(output, list):
        raise Exception('output is not list')

    for i in output:
        if not hasattr(Manufacturers, i):
            raise Exception("{0} is not a valid attribute".format(i))

    order_by = ("desc", "asc")
    order_list = order.split()

    if not hasattr(Manufacturers, order_list[0]):
        raise Exception("{0} is not a valid attribute".format(order_list[0]))
    if order_list[1] not in order_by:
        raise Exception("{0} is not a valid value".format(order_list[1]))

    if not isinstance(limit, int):
        raise Exception("{0} is not a valid value".format(limit))

    order_obj = getattr(getattr(Manufacturers, order_list[0]), order_list[1])


    if where:
        man_list = db.session.query(Manufacturers).filter_by(**where).order_by(order_obj()).limit(limit).all()
    else:
        man_list = db.session.query(Manufacturers).order_by(order_obj()).limit(limit).all()


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
        return [output_func(x, output) for x in man_list]
    else:
        return [general_output(x) for x in man_list]


def update(**kwargs):
    where = kwargs.get("where", {})
    data = kwargs.get("data", {})
    if not ("id" in where and where.get("id", None)):
        raise Exception("id not included")

    for x, y in data.iteritems():
        if not (hasattr(Manufacturers, x) and y):
            raise Exception("data wrong")
    man = db.session.query(Manufacturers).filter_by(**where).update(data)

    try:
        db.session.commit()
    except Exception as e:
        print e

    return man


def delete(**kwargs):
    where = kwargs.get("where", {})
    if not("id" in where and where.get("id", None)):
        raise Exception("id not included")
    man = db.session.query(Manufacturers).filter_by(**where).all()

    if man:
        try:
            db.session.delete(man[0])
            db.session.commit()
        except Exception as e:
            print e
    else:
        raise Exception("id not in db")

    id = man[0].id
    man = db.session.query(Manufacturers).filter_by(id=id).all()
    if man:
        return id
