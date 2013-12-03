import xml.etree.ElementTree as ET
from models import EnterpriseModel, JobModel, EmailModel, JobMetaModel
from flask import flash

def import_enterprise(content):
    """

    Arguments:
    - `content`: string
    """
    root = ET.fromstring(content)
    for e in root.iter('enterprise'):
        name = e.get('name')
        shortname = e.get('shortname')
        model = EnterpriseModel.query(EnterpriseModel.name==name).get()
        if not model:
            model = EnterpriseModel(
                name = name,
                shortname = shortname
            )
            model.put()

        emails = e.find('emails')
        for email in emails.iter('email'):
            if not email.text or len(email.text) == 0:
                continue

            mail = EmailModel.query(EmailModel.enterprise==model.key, EmailModel.email==email.text).get()
            if not mail:
                mail = EmailModel(
                    enterprise = model.key,
                    email = email.text
                )
                mail.put()
    return 0

def export_enterprise():
    enterprises = EnterpriseModel().query()
    root = ET.Element('enterprises')
    for enterprise in enterprises:
        e = ET.Element('enterprise')
        e.set('name', enterprise.name)
        e.set('shortname', enterprise.shortname)
        root.append(e)

        sub = ET.SubElement(e, 'emails')
        emails = EmailModel.query(EmailModel.enterprise==enterprise.key)

        for email in emails:
            element = ET.Element('email')
            element.text = email.email
            sub.append(element)
    return ET.tostring(root)


def import_jobs(content):
    """

    Arguments:
    - `content`:
    """
    root = ET.fromstring(content)
    for job in root.iter('job'):
        jobtype = job.get('type')
        fr = {
            'published': False,
            'title': '',
            'content': ''
        }
        en = {
            'published': False,
            'title': '',
            'content': ''
        }
        zh = {
            'published': False,
            'title': '',
            'content': ''
        }

        meta = {
            'en': en,
            'fr': fr,
            'zh': zh
        }
        for m in job.iter('meta'):
            lang = m.get('lang')
            title = m.find('title').text
            content = m.find('content').text
            l = meta[lang]
            l['published'] = True
            l['title'] = title
            l['content'] = content

        online = job.get('online')
        apply_info = job.find('apply')
        if int(online) == 0:
            enterprise = apply_info.find('enterprise').text
            email = apply_info.find('email').text

            e = EnterpriseModel.query(EnterpriseModel.name==enterprise).get()
            e_email = EmailModel.query(EmailModel.enterprise==e.key, EmailModel.email==email).get()

            j = JobModel(
                type = jobtype,
                is_online = False,
                is_complete = True,
                enterprise = e.key,
                enterprise_email = e_email.key,
                meta = meta,
                published = True,
                default_lang = 'en',
                cv_required = ['en']
            )
        else:
            url = apply_info.find('url').text
            j = JobModel(
                type = jobtype,
                is_online = True,
                is_complete = False,
                apply_url = url,
                meta = meta,
                published = True,
                default_lang = 'en',
                cv_required = ['en']
            )
        j.put()
    return 0
