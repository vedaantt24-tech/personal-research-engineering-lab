import os, sys
os.environ.setdefault('DATABASE_URL','sqlite:////tmp/personal-lab-test.db')
os.environ.setdefault('OWNER_EMAIL','owner@example.com')
os.environ.setdefault('OWNER_PASSWORD','change-this-password')
os.environ.setdefault('SECRET_KEY','test-secret-key-123456789012345678901234')
os.environ.setdefault('AUTO_CREATE_TABLES','true')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine
from app.models.entities import AgreementTemplate

Base.metadata.drop_all(engine); Base.metadata.create_all(engine)

def login(c):
    response=c.post('/api/v1/auth/login',json={'email':'owner@example.com','password':'change-this-password'})
    assert response.status_code==200
    csrf=c.cookies.get('csrf_token'); assert csrf
    return {'X-CSRF-Token':csrf}

def test_owner_permission_and_controlled_access_flow():
    with TestClient(app) as c:
        headers=login(c)
        ag=c.get('/api/v1/public/agreements/IDEA_EVALUATION').json()
        terms=c.get('/api/v1/public/agreements/SITE_TERMS').json()
        created=c.post('/api/v1/admin/content/ideas',headers=headers,json={'public_id':'IDEA-TEST-1','slug':'test-idea','title':'Test Idea','one_line':'Test concept','question':'Could this work?','problem':'A real problem','proposed_concept':'High-level concept','status':'CONCEPT','visibility':'PUBLIC','state':'PUBLISHED','requires_permission':True,'publication_safety_confirmed':True,'how_it_works':'Private detail','required_technology':'Private stack'})
        assert created.status_code==200
        req=c.post('/api/v1/collaboration-requests',json={'name':'Tester','email':'tester@example.com','professional_profile_url':'https://example.com/profile','website_url':'https://example.com','purpose':'Prototype evaluation','requested_rights':['Concept','Technical documentation'],'agreement_type':ag['agreement_type'],'agreement_version':ag['version'],'agreement_sha256':ag['sha256'],'site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],'privacy_acknowledged':True,'idea_public_id':'IDEA-TEST-1','signature_name':'Tester'})
        assert req.status_code==201
        rid=req.json()['request_id']
        detail=c.get('/api/v1/public/ideas/test-idea').json()
        assert detail['one_line']=='Test concept'
        assert 'how_it_works' not in detail and 'required_technology' not in detail
        approved=c.patch(f'/api/v1/admin/requests/{rid}',headers=headers,json={'status':'APPROVED'})
        assert approved.status_code==200 and approved.json()['permission_granted'] is True
        link=c.post(f'/api/v1/admin/requests/{rid}/access-link',headers=headers,json={'expires_days':2})
        assert link.status_code==200
        shared=c.get(link.json()['access_path'])
        assert shared.status_code==200
        assert shared.json()['idea']['how_it_works']=='Private detail'
        assert shared.json()['request_id']==rid
        logs=c.get('/api/v1/admin/audit-logs',headers=headers).json()
        assert any(x['action']=='RESTRICTED_ACCESS_USED' and x['entity_type']=='PermissionGrant' for x in logs)
        revoked=c.delete(f'/api/v1/admin/requests/{rid}/access-link',headers=headers)
        assert revoked.status_code==200
        assert c.get(link.json()['access_path']).status_code==404


def test_public_publish_requires_safety_and_relations_work():
    with TestClient(app) as c:
        headers=login(c)
        denied=c.post('/api/v1/admin/content/projects',headers=headers,json={'slug':'proj','title':'Project','summary':'High level','visibility':'PUBLIC','state':'PUBLISHED'})
        assert denied.status_code==409
        allowed=c.post('/api/v1/admin/content/projects',headers=headers,json={'slug':'proj','title':'Project','summary':'High level','visibility':'PUBLIC','state':'PUBLISHED','publication_safety_confirmed':True})
        assert allowed.status_code==200
        pid=allowed.json()['id']
        tech=c.put(f'/api/v1/admin/projects/{pid}/technologies',headers=headers,json={'technologies':['Python','FastAPI','Python']})
        assert tech.status_code==200 and [x['technology'] for x in tech.json()]==['Python','FastAPI']
        public=c.get(f'/api/v1/public/projects/{pid}/technologies')
        assert public.status_code==200 and public.json()==['Python','FastAPI']
        rid=c.post('/api/v1/admin/content/research',headers=headers,json={'slug':'research-1','title':'Research','visibility':'PUBLIC','state':'PUBLISHED','publication_safety_confirmed':True}).json()['id']
        refs=c.put(f'/api/v1/admin/research/{rid}/references',headers=headers,json={'references':[{'title':'Paper A','authors':'Author','venue':'Venue','year':2026,'url':'https://example.com/paper'}]})
        assert refs.status_code==200 and refs.json()[0]['title']=='Paper A'
        public_refs=c.get(f'/api/v1/public/research/{rid}/references')
        assert public_refs.status_code==200 and public_refs.json()[0]['year']==2026


def test_unlisted_is_direct_only_and_agreement_versions_are_immutable():
    with TestClient(app) as c:
        headers=login(c)
        created=c.post('/api/v1/admin/content/ideas',headers=headers,json={'public_id':'IDEA-UNLISTED','slug':'unlisted','title':'Unlisted','one_line':'Direct link only','status':'CONCEPT','visibility':'UNLISTED','state':'PUBLISHED'})
        assert created.status_code==200
        listing=c.get('/api/v1/public/ideas').json()
        assert not any(x.get('slug')=='unlisted' for x in listing)
        assert c.get('/api/v1/public/ideas/unlisted').status_code==200
        ags=c.get('/api/v1/admin/agreements',headers=headers).json()
        aid=next(x['id'] for x in ags if x['agreement_type']=='IDEA_EVALUATION')
        resp=c.patch(f'/api/v1/admin/agreements/{aid}',headers=headers,json={'body':'changed'})
        assert resp.status_code==409


def test_contact_audit_media_and_real_analytics():
    with TestClient(app) as c:
        response=c.post('/api/v1/analytics/event',json={'event_type':'page_view','path':'/ideas'})
        assert response.status_code==202
        terms=c.get('/api/v1/public/agreements/SITE_TERMS').json()
        contact=c.post('/api/v1/contact',json={'name':'Visitor','email':'visitor@example.com','organization':'Org','message':'Hello','website':'','site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],'privacy_acknowledged':True})
        assert contact.status_code==200
        headers=login(c)
        summary=c.get('/api/v1/admin/summary').json()
        assert summary['page_views_30d'] >= 1 and summary['unread_messages'] >= 1
        messages=c.get('/api/v1/admin/messages',headers=headers).json()
        assert messages[0]['network_ip_hash']
        assert messages[0]['site_terms_body_snapshot']==terms['body']
        media=c.post('/api/v1/admin/media',headers=headers,files={'file':('demo.txt',b'hello world','text/plain')},data={'visibility':'PUBLIC'})
        assert media.status_code==200 and media.json()['public_url']
        public_url=media.json()['public_url']
        assert c.get(public_url).status_code==200
        listing=c.get('/api/v1/admin/media',headers=headers)
        assert listing.status_code==200 and listing.json()[0]['sha256']
        project=c.post('/api/v1/admin/content/projects',headers=headers,json={'slug':'media-project','title':'Media Project','summary':'Public project','visibility':'PUBLIC','state':'PUBLISHED','publication_safety_confirmed':True})
        assert project.status_code==200
        pid=project.json()['id']
        attach=c.put(f'/api/v1/admin/media-links/project/{pid}',headers=headers,json={'media_ids':[media.json()['id']]})
        assert attach.status_code==200 and attach.json()[0]['media_id']==media.json()['id']
        links=c.get(f'/api/v1/public/media-links/project/{pid}')
        assert links.status_code==200 and links.json()[0]['filename']=='demo.txt'

def test_experiment_data_resume_and_optional_github_endpoint():
    with TestClient(app) as c:
        headers=login(c)
        exp=c.post('/api/v1/admin/content/experiments',headers=headers,json={'slug':'lab-exp','title':'Measured Experiment','visibility':'PUBLIC','state':'PUBLISHED','publication_safety_confirmed':True}).json()
        eid=exp['id']
        saved=c.put(f'/api/v1/admin/experiments/{eid}/data',headers=headers,json={'data':[
            {'series':'trial-a','x_label':'1','x_value':1,'y_value':0.4,'unit':'V'},
            {'series':'trial-a','x_label':'2','x_value':2,'y_value':0.7,'unit':'V'},
        ]})
        assert saved.status_code==200 and len(saved.json())==2
        public=c.get(f'/api/v1/public/experiments/{eid}/data')
        assert public.status_code==200 and public.json()[1]['y_value']==0.7
        gh=c.get('/api/v1/public/github')
        assert gh.status_code==200 and gh.json()['configured'] is False
        generated=c.post('/api/v1/admin/resume/generate',headers=headers)
        assert generated.status_code==200
        assert generated.json()['file_url'].startswith('/api/v1/public/media/')
        active_resume=c.get('/api/v1/public/resume')
        assert active_resume.status_code==200 and active_resume.json()['active'] is True and active_resume.json()['state']=='PUBLISHED'

def test_public_search_only_returns_published_public_content_and_logout_clears_csrf():
    with TestClient(app) as c:
        headers=login(c)
        hidden=c.post('/api/v1/admin/content/projects',headers=headers,json={'slug':'private-search','title':'Secret Search Project','summary':'Hidden','visibility':'PRIVATE','state':'DRAFT'})
        assert hidden.status_code==200
        public=c.post('/api/v1/admin/content/projects',headers=headers,json={'slug':'searchable','title':'Searchable Engineering Project','summary':'Build systems','visibility':'PUBLIC','state':'PUBLISHED','publication_safety_confirmed':True})
        assert public.status_code==200
        result=c.get('/api/v1/public/search?q=searchable').json()
        assert any(r['title']=='Searchable Engineering Project' for r in result['results'])
        assert not any(r['title']=='Secret Search Project' for r in result['results'])
        assert c.cookies.get('csrf_token')
        out=c.post('/api/v1/auth/logout',headers=headers)
        assert out.status_code==200
        assert not c.cookies.get('csrf_token')

def test_revisions_are_append_only_and_agreement_snapshot_is_preserved():
    with TestClient(app) as c:
        assert c.get('/api/v1/health/live').status_code == 200
        assert c.get('/api/v1/health/ready').status_code == 200
        agreement = c.get('/api/v1/public/agreements/IDEA_EVALUATION').json()
        headers = login(c)
        created = c.post('/api/v1/admin/content/projects', headers=headers, json={
            'slug':'revision-test','title':'Revision Test','summary':'Initial','visibility':'PRIVATE','state':'DRAFT'
        })
        assert created.status_code == 200
        project_id = created.json()['id']
        revisions1 = c.get(f'/api/v1/admin/content/projects/{project_id}/revisions', headers=headers)
        assert revisions1.status_code == 200 and len(revisions1.json()) == 1
        updated = c.put(f'/api/v1/admin/content/projects/{project_id}', headers=headers, json={'summary':'Changed','change_note':'Updated measured summary'})
        assert updated.status_code == 200
        revisions2 = c.get(f'/api/v1/admin/content/projects/{project_id}/revisions', headers=headers).json()
        assert len(revisions2) == 2 and revisions2[0]['version_no'] == 2 and revisions2[0]['change_note'] == 'Updated measured summary'
        restored = c.post(f"/api/v1/admin/content/projects/{project_id}/restore/{revisions2[1]['id']}", headers=headers)
        assert restored.status_code == 200 and restored.json()['summary'] == 'Initial'
        revisions3 = c.get(f'/api/v1/admin/content/projects/{project_id}/revisions', headers=headers).json()
        assert len(revisions3) == 3 and revisions3[0]['version_no'] == 3
        request_payload = {
            'name':'Revision User','email':'revision@example.com','purpose':'Evaluate the concept','requested_rights':['Concept'],
            'signature_name':'Revision User','agreement_type':agreement['agreement_type'],'agreement_version':agreement['version'],
            'agreement_sha256':agreement['sha256'],'site_terms_version':c.get('/api/v1/public/agreements/SITE_TERMS').json()['version'],'site_terms_sha256':c.get('/api/v1/public/agreements/SITE_TERMS').json()['sha256'],'privacy_acknowledged':True,'message':'Please contact me.'
        }
        req = c.post('/api/v1/collaboration-requests', json=request_payload)
        assert req.status_code == 201
        requests = c.get('/api/v1/admin/requests', headers=headers).json()
        match = next(x for x in requests if x['request_id'] == req.json()['request_id'])
        assert match['agreement_body_snapshot'] == agreement['body']


def test_auxiliary_content_uses_unified_workflow_and_public_filters():
    with TestClient(app) as c:
        headers=login(c)
        created=c.post('/api/v1/admin/content/skills',headers=headers,json={'category':'AI/ML','name':'Private Skill','level':'Learning','published':True,'state':'DRAFT'})
        assert created.status_code==200
        sid=created.json()['id']
        assert not any(x['name']=='Private Skill' for x in c.get('/api/v1/public/skills').json())
        revisions=c.get(f'/api/v1/admin/content/skills/{sid}/revisions',headers=headers)
        assert revisions.status_code==200 and len(revisions.json())==1
        updated=c.put(f'/api/v1/admin/content/skills/{sid}',headers=headers,json={'state':'PUBLISHED','publication_safety_confirmed':True,'change_note':'Made public after review'})
        assert updated.status_code==200
        assert any(x['name']=='Private Skill' for x in c.get('/api/v1/public/skills').json())
        revisions2=c.get(f'/api/v1/admin/content/skills/{sid}/revisions',headers=headers).json()
        assert len(revisions2)==2 and revisions2[0]['change_note']=='Made public after review'


def test_restricted_permission_scope_filters_fields_and_owner_is_single_account():
    with TestClient(app) as c:
        headers=login(c)
        denied=c.put('/api/v1/admin/profile',json={'tagline':'nope'})
        assert denied.status_code in {401,403}
        created=c.post('/api/v1/admin/content/ideas',headers=headers,json={'public_id':'IDEA-SCOPE','slug':'scope-test','title':'Scoped Idea','one_line':'High level','question':'Q','problem':'P','current_approach':'C','proposed_concept':'Concept','how_it_works':'Implementation detail','required_technology':'Private stack','assumptions':'Assumption','risks':'Risk','open_questions':'Open','applications':'Application','prototype_status':'planned','visibility':'PUBLIC','state':'PUBLISHED','requires_permission':True,'publication_safety_confirmed':True})
        assert created.status_code==200
        ag=c.get('/api/v1/public/agreements/IDEA_EVALUATION').json(); terms=c.get('/api/v1/public/agreements/SITE_TERMS').json()
        req=c.post('/api/v1/collaboration-requests',json={'name':'Scope Tester','email':'scope@example.com','purpose':'Concept review','requested_rights':['Concept'],'signature_name':'Scope Tester','agreement_type':ag['agreement_type'],'agreement_version':ag['version'],'agreement_sha256':ag['sha256'],'site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],'privacy_acknowledged':True,'idea_public_id':'IDEA-SCOPE'})
        assert req.status_code==201
        rid=req.json()['request_id']
        assert c.patch(f'/api/v1/admin/requests/{rid}',headers=headers,json={'status':'APPROVED'}).status_code==200
        link=c.post(f'/api/v1/admin/requests/{rid}/access-link',headers=headers,json={'expires_days':1}).json()
        shared=c.get(link['access_path'])
        assert shared.status_code==200
        data=shared.json()['idea']
        assert data['proposed_concept']=='Concept'
        assert 'how_it_works' not in data and 'required_technology' not in data and 'risks' not in data


def test_achievement_public_publish_requires_safety_and_searches():
    with TestClient(app) as c:
        headers=login(c)
        denied=c.post('/api/v1/admin/content/achievements',headers=headers,json={'title':'Achievement','published':True,'state':'PUBLISHED'})
        assert denied.status_code==409
        created=c.post('/api/v1/admin/content/achievements',headers=headers,json={'title':'Verified Achievement','published':True,'state':'PUBLISHED','publication_safety_confirmed':True})
        assert created.status_code==200
        public=c.get('/api/v1/public/achievements').json()
        assert any(x['title']=='Verified Achievement' for x in public)
        result=c.get('/api/v1/public/search?q=Verified%20Achievement').json()
        achievement = next(x for x in result['results'] if x['type']=='achievement')
        assert achievement['url']=='/about#achievements'

def test_profile_email_is_private_by_default_then_explicitly_public():
    with TestClient(app) as c:
        login(c)
        private = c.get('/api/v1/public/profile').json()
        assert private.get('contact_email') is None
        headers = login(c)
        updated = c.put('/api/v1/admin/profile', headers=headers, json={'contact_email':'public@example.com','contact_email_public':True})
        assert updated.status_code==200
        public = c.get('/api/v1/public/profile').json()
        assert public['contact_email']=='public@example.com' and public['contact_email_public'] is True


def test_timeline_is_first_class_content_and_public_only_after_publish():
    with TestClient(app) as c:
        headers=login(c)
        created=c.post('/api/v1/admin/content/timeline',headers=headers,json={'date_label':'2026','title':'Started research lab','category':'Milestone','description':'Created the platform foundation','state':'DRAFT','published':True})
        assert created.status_code==200
        assert not any(x['title']=='Started research lab' for x in c.get('/api/v1/public/timeline').json())
        tid=created.json()['id']
        published=c.put(f'/api/v1/admin/content/timeline/{tid}',headers=headers,json={'state':'PUBLISHED','published':True,'publication_safety_confirmed':True})
        assert published.status_code==200
        assert any(x['title']=='Started research lab' for x in c.get('/api/v1/public/timeline').json())
        revisions=c.get(f'/api/v1/admin/content/timeline/{tid}/revisions',headers=headers).json()
        assert len(revisions)>=2


def test_invalid_collaboration_right_is_rejected():
    with TestClient(app) as c:
        ag=c.get('/api/v1/public/agreements/IDEA_EVALUATION').json(); terms=c.get('/api/v1/public/agreements/SITE_TERMS').json()
        req=c.post('/api/v1/collaboration-requests',json={'name':'Invalid Right','email':'invalid@example.com','purpose':'Testing unsupported permission','requested_rights':['Delete the internet'],'signature_name':'Invalid Right','agreement_type':ag['agreement_type'],'agreement_version':ag['version'],'agreement_sha256':ag['sha256'],'site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],'privacy_acknowledged':True})
        assert req.status_code==422


def test_public_media_path_traversal_does_not_escape_storage():
    with TestClient(app) as c:
        headers=login(c)
        response=c.get('/api/v1/public/media/../../../../etc/passwd')
        assert response.status_code in {400,404}


def test_investor_and_funding_request_types_are_recorded_and_require_designated_agreements():
    with TestClient(app) as c:
        ag_inv=c.get('/api/v1/public/agreements/INVESTOR_DISCUSSION').json()
        ag_fund=c.get('/api/v1/public/agreements/FUNDING_REQUEST').json()
        terms=c.get('/api/v1/public/agreements/SITE_TERMS').json()
        investor=c.post('/api/v1/collaboration-requests',json={
            'request_kind':'INVESTOR_OUTREACH','name':'Investor','email':'investor@example.com',
            'purpose':'Discuss strategic investment interest','requested_rights':['Collaboration'],
            'signature_name':'Investor','agreement_type':ag_inv['agreement_type'],'agreement_version':ag_inv['version'],
            'agreement_sha256':ag_inv['sha256'],'site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],
            'privacy_acknowledged':True,'investment_interest':'Interested in seed/strategic investment.'
        })
        assert investor.status_code==201
        funding=c.post('/api/v1/collaboration-requests',json={
            'request_kind':'FUNDING_REQUEST','name':'Founder','email':'founder@example.com',
            'purpose':'Seeking funding for an engineering prototype','requested_rights':['Collaboration'],
            'signature_name':'Founder','agreement_type':ag_fund['agreement_type'],'agreement_version':ag_fund['version'],
            'agreement_sha256':ag_fund['sha256'],'site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],
            'privacy_acknowledged':True,'funding_amount':250000,'funding_currency':'INR',
            'funding_stage':'Prototype','funding_instrument':'Grant','funding_use':'Build and test prototype',
            'pitch_deck_url':'https://example.com/deck'
        })
        assert funding.status_code==201
        headers=login(c)
        rows=c.get('/api/v1/admin/requests',headers=headers).json()
        by_id={r['request_id']:r for r in rows}
        inv=by_id[investor.json()['request_id']]
        fund=by_id[funding.json()['request_id']]
        assert inv['request_kind']=='INVESTOR_OUTREACH' and 'strategic investment' in inv['investment_interest']
        assert fund['request_kind']=='FUNDING_REQUEST' and fund['funding_amount']==250000 and fund['funding_currency']=='INR'
        bad=c.post('/api/v1/collaboration-requests',json={
            'request_kind':'FUNDING_REQUEST','name':'Bad','email':'bad@example.com','purpose':'Funding','requested_rights':['Collaboration'],
            'signature_name':'Bad','agreement_type':ag_inv['agreement_type'],'agreement_version':ag_inv['version'],
            'agreement_sha256':ag_inv['sha256'],'site_terms_version':terms['version'],'site_terms_sha256':terms['sha256'],
            'privacy_acknowledged':True,'funding_amount':1
        })
        assert bad.status_code==422

def test_public_social_links_returns_published_owner_configured_links():
    with TestClient(app) as c:
        headers=login(c)
        for payload in [
            {'platform':'Instagram','url':'https://instagram.com/example','label':'Instagram','published':True,'state':'PUBLISHED','publication_safety_confirmed':True},
            {'platform':'LinkedIn','url':'https://linkedin.com/in/example','label':'LinkedIn','published':True,'state':'PUBLISHED','publication_safety_confirmed':True},
            {'platform':'Private Network','url':'https://private.example/profile','label':'Private','published':False,'state':'DRAFT'},
        ]:
            r=c.post('/api/v1/admin/content/social-links',headers=headers,json=payload)
            assert r.status_code==200
        rows=c.get('/api/v1/public/social-links').json()
        assert any(x['platform']=='Instagram' and x['url'].startswith('https://instagram.com') for x in rows)
        assert any(x['platform']=='LinkedIn' for x in rows)
        assert not any(x['platform']=='Private Network' for x in rows)

def test_social_links_support_multiple_published_platforms_and_reject_unsafe_urls():
    with TestClient(app) as c:
        headers=login(c)
        for platform, url in [
            ('Instagram','https://instagram.com/example'),
            ('LinkedIn','https://linkedin.com/in/example'),
            ('YouTube','https://youtube.com/@example'),
            ('Custom Lab','https://example.org/connect'),
        ]:
            r=c.post('/api/v1/admin/content/social-links',headers=headers,json={'platform':platform,'url':url,'label':platform,'published':True,'state':'PUBLISHED','publication_safety_confirmed':True})
            assert r.status_code==200
        unsafe=c.post('/api/v1/admin/content/social-links',headers=headers,json={'platform':'Bad','url':'javascript:alert(1)','label':'Bad','published':True,'state':'PUBLISHED','publication_safety_confirmed':True})
        assert unsafe.status_code==422
        rows=c.get('/api/v1/public/social-links').json()
        assert {x['platform'] for x in rows} >= {'Instagram','LinkedIn','YouTube','Custom Lab'}


def test_visibility_settings_are_owner_controlled():
    with TestClient(app) as c:
        headers=login(c)
        public=c.get('/api/v1/admin/visibility-settings',headers=headers)
        assert public.status_code==200
        saved=c.put('/api/v1/admin/visibility-settings/projects',headers=headers,json={'default_visibility':'PUBLIC','notes':'Public publishing still requires the safety confirmation.'})
        assert saved.status_code==200
        assert saved.json()['default_visibility']=='PUBLIC'
        rows=c.get('/api/v1/admin/visibility-settings',headers=headers).json()
        assert any(x['key']=='projects' and x['default_visibility']=='PUBLIC' for x in rows)
