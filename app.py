"""UdyamOne: catalogue-backed MSME onboarding demo."""
import json
import sqlite3
import uuid
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data.loaders import load_catalogue, load_gstin_registry, load_udyam_registry, load_analytics
from src.engines.eligibility_engine import evaluate_product
from src.engines.pricing_engine import calculate_quote
from src.engines.recommendation_engine import recommend
from src.database.repository import save_business, save_quote, revise_quote, list_quotes, get_order, update_order, save_kyc_result
from src.database.connection import initialize
from src.services.registry_service import verify_gstin, verify_udyam
from src.services.order_service import accept_quote_checked, record_kyc_outcome
from src.services.consent_service import record_registry_consent, registry_consent_granted
from src.integrations.demo_documents import make_sample_pdf
from src.utils.formatters import inr
from src.utils.upload_validation import validate_specimen_upload
from src.utils.validators import validate_business_profile
from src.config.settings import MAX_UPLOAD_BYTES

st.set_page_config(page_title="UdyamOne | Airtel Business", page_icon="🔴", layout="wide", initial_sidebar_state="expanded")
from pathlib import Path
st.markdown(f"<style>{(Path(__file__).parent / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",unsafe_allow_html=True)
try:
    initialize()
    catalogue=load_catalogue()
    load_gstin_registry()
    load_udyam_registry()
except (sqlite3.Error, OSError):
    st.error("Demo storage could not be initialized. Check that the configured SQLite path is writable, then restart the app.")
    st.stop()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"Required demo data could not be loaded: {exc}")
    st.stop()

TEXT={"English":{"Overview":"Overview","AI Business Advisor":"AI Business Advisor","Product Catalogue":"Product Catalogue","Bundle Builder":"Bundle Builder","Quotes & Orders":"Quotes & Orders","Smart KYC":"Smart KYC","Order Tracker":"Order Tracker","Operations Dashboard":"Operations Dashboard","Settings":"Settings"},
"हिन्दी":{"Overview":"अवलोकन","AI Business Advisor":"AI व्यवसाय सलाहकार","Product Catalogue":"उत्पाद सूची","Bundle Builder":"बंडल बनाएँ","Quotes & Orders":"कोटेशन और ऑर्डर","Smart KYC":"स्मार्ट KYC","Order Tracker":"ऑर्डर ट्रैकर","Operations Dashboard":"ऑपरेशन डैशबोर्ड","Settings":"सेटिंग्स"}}
SEGMENT_LABELS={"micro":"Micro business","prof":"Professional office","multi":"Multi-location business","mfg":"Manufacturer"}
if "language" not in st.session_state: st.session_state.language="English"
if "profile" not in st.session_state: st.session_state.profile={"id":str(uuid.uuid4()),"business_name":"","business_type":"","segment":"micro","city":"","state":"","city_tier":1,"employees":1,"sites":1,"budget":None,"has_gstin":False,"selected_ids":[]}
for widget_key,profile_key,default in [("profile_name","business_name",""),("profile_kind","business_type",""),("profile_city","city",""),("profile_state","state",""),("profile_segment","segment","micro"),("profile_tier","city_tier",1),("profile_employees","employees",1),("profile_sites","sites",1),("profile_budget","budget",0),("profile_has_gstin","has_gstin",False)]:
    st.session_state.setdefault(widget_key,st.session_state.profile.get(profile_key) if st.session_state.profile.get(profile_key) is not None else default)
if "bundle" not in st.session_state: st.session_state.bundle={}
if "active_quote" not in st.session_state: st.session_state.active_quote=None
if "active_order" not in st.session_state: st.session_state.active_order=None
lang=st.session_state.language

with st.sidebar:
    st.markdown('<div class="brand">UdyamOne<span style="color:white">.</span></div>',unsafe_allow_html=True)
    st.caption("AIRTEL BUSINESS · MSME SERVICES")
    st.divider()
    pages=list(TEXT[lang].keys())
    page=st.radio("Workspace",pages,label_visibility="collapsed",format_func=lambda x:TEXT[lang][x])
    st.divider()
    st.selectbox("Language / भाषा",["English","हिन्दी"],key="language")
    st.caption("DEMO MODE · Mock registries and simulated fulfilment")
    if st.button("Load synthetic clinic demo",help="Loads a sample clinic profile, compatible bundle and mock-registry identifiers."):
        st.session_state.profile.update({"business_name":"Balaji Dental Care LLP","business_type":"Dental clinic","segment":"prof","city":"Kochi","state":"Kerala","city_tier":2,"employees":4,"sites":1,"budget":4000,"has_gstin":True})
        for widget_key,value in [("profile_name","Balaji Dental Care LLP"),("profile_kind","Dental clinic"),("profile_city","Kochi"),("profile_state","Kerala"),("profile_segment","prof"),("profile_tier",2),("profile_employees",4),("profile_sites",1),("profile_budget",4000),("profile_has_gstin",True)]: st.session_state[widget_key]=value
        st.session_state.kyc_gstin="32TTNXB7384T1ZW"; st.session_state.kyc_udyam="UDYAM-KL-00-3078801"
        st.session_state.bundle={"P01":1,"P12":1,"P16":4}
        save_business(st.session_state.profile)
        st.toast("Synthetic clinic profile and starter bundle loaded")

def heading(title, subtitle=""):
    st.markdown(f'<div class="eyebrow">UDYAMONE · AIRTEL BUSINESS</div><h1 style="margin:.15rem 0 .2rem">{title}</h1><p class="muted">{subtitle}</p>',unsafe_allow_html=True)
def set_profile(form):
    st.session_state.profile.update(form); save_business(st.session_state.profile)
def advance_order(order_id,status,note):
    try:
        update_order(order_id,status,note)
        st.session_state.tracked_order=get_order(order_id)
        st.rerun()
    except ValueError as exc:
        st.error(f"The demo order could not move to {status}: {exc}")
if page=="Overview":
    st.markdown('<div class="eyebrow">THE BUSINESS JOURNEY, MADE SIMPLE</div>',unsafe_allow_html=True)
    st.markdown('<div class="hero"><div class="eyebrow" style="color:#ff8096">WELCOME TO UDYAMONE</div><h1>Business services, made<br>easier to choose.</h1><p>Tell us how your business works. Explore catalogue-backed connectivity and digital services, build a bundle, review indicative pricing, and follow a demo onboarding journey.</p><span class="step">Discover</span><span class="step">Understand</span><span class="step">Build</span><span class="step">Track</span></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for col,title,desc in [(c1,"Guided recommendations","A deterministic advisor uses your profile and the supplied product rules."),(c2,"Transparent pricing","Quotes use catalogue starting prices and setup fees. No unlisted taxes or discounts."),(c3,"A connected workflow","Save a quote, record demo consent, validate identifiers against mock registries, and track the order.")]:
        with col: st.markdown(f'<div class="card"><b>{title}</b><p class="muted">{desc}</p></div>',unsafe_allow_html=True)
    st.markdown("### Start with your business")
    p=st.session_state.profile
    with st.form("overview_profile"):
        a,b,c=st.columns(3); name=a.text_input("Business name",key="profile_name"); kind=b.text_input("Business type",key="profile_kind"); city=c.text_input("City",key="profile_city")
        d,e,f=st.columns(3); state=d.text_input("State",key="profile_state"); seg=e.selectbox("Business type group",["micro","prof","multi","mfg"],format_func=lambda value:SEGMENT_LABELS[value],key="profile_segment"); tier=f.selectbox("Catalogue city tier",[1,2],format_func=lambda value:f"Tier {value}",key="profile_tier",help="This uses the product catalogue's tier values. A city-to-tier lookup is not included in the supplied data.")
        g,h,i=st.columns(3); employees=g.number_input("Employees",1,100000,key="profile_employees"); sites=h.number_input("Business locations",1,10000,key="profile_sites"); budget=i.number_input("Monthly budget (₹, optional)",0,10000000,step=500,key="profile_budget")
        gst=st.checkbox("I have a GSTIN",key="profile_has_gstin")
        if st.form_submit_button("Save business profile",type="primary"):
            submitted_profile={"business_name":name.strip(),"business_type":kind.strip(),"city":city.strip(),"state":state.strip(),"segment":seg,"city_tier":tier,"employees":employees,"sites":sites,"budget":budget or None,"has_gstin":gst}
            valid,errors=validate_business_profile(submitted_profile)
            if valid: set_profile(submitted_profile); st.success("Profile saved for this demo business.")
            else: st.error("Please complete: "+", ".join(errors)+".")
    st.info("Demo environment. Registry lookups use the supplied mock datasets; order updates are simulated and do not connect to Airtel systems.")

elif page=="AI Business Advisor":
    heading("AI Business Advisor","A guided, rules-based discovery flow. No LLM is configured; recommendations come directly from the catalogue and eligibility rules.")
    p=st.session_state.profile
    st.markdown("### Tell us what you need")
    with st.form("advisor_form"):
        a,b=st.columns(2); objective=a.selectbox("Main goal",["Reliable internet","Talk to more customers","Protect devices and business data","Manage multiple locations","Digitise billing and operations"]); existing=b.text_input("What do you use today? (optional)")
        budget=st.number_input("Monthly spend comfort (₹)",0,1000000,int(p.get("budget") or 0),step=500)
        profile_ready,_=validate_business_profile(p)
        submitted=st.form_submit_button("Get recommendations",type="primary",disabled=not profile_ready)
    if not profile_ready: st.info("Save your business name, type, city and state on Overview to receive profile-based recommendations.")
    if submitted:
        p["budget"]=budget or None; p["existing_services"]=existing.strip(); st.session_state.profile=p; save_business(p)
        recs=recommend(catalogue,p,budget or None)
        selected_categories={"Reliable internet":["Connectivity"],"Talk to more customers":["Communication"],"Protect devices and business data":["Security","Cloud & Productivity"],"Manage multiple locations":["Connectivity","Security"],"Digitise billing and operations":["Cloud & Productivity","IoT & Physical"]}[objective]
        recs=[r for r in recs if r["product"]["category"] in selected_categories]
        st.session_state.recommendations=[r["product"]["product_id"] for r in recs]
        st.markdown(f"### Recommendations for {p.get('business_name') or 'your business'}")
        if not recs: st.warning("No catalogue products match this profile and goal. Review your business details or explore the full catalogue.")
        for item in recs[:8]:
            prod=item["product"]; st.markdown(f"**{prod['product_name']}** · {item['status']} · from {inr(item['monthly_from'])}/month  \n{item['why']}  \n{item['eligibility']['missing'] and 'Needs: '+', '.join(item['eligibility']['missing']) or 'Meets the supplied catalogue rules.'}")
            if st.button(f"Add {prod['product_id']} to bundle",key=f"advisor_{prod['product_id']}"):
                st.session_state.bundle[prod["product_id"]]=st.session_state.bundle.get(prod["product_id"],0)+1; st.toast("Added to bundle")
    if st.button("Restart discovery"):
        st.session_state.pop("recommendations",None); st.rerun()

elif page=="Product Catalogue":
    heading("Product catalogue","Explore the 25 products in the supplied catalogue. Availability and requirements come from its published fields.")
    category=st.selectbox("Category",["All categories"]+sorted(catalogue.category.unique())); search=st.text_input("Search products",placeholder="Try fibre, WhatsApp, security…")
    products=catalogue.copy()
    if category!="All categories": products=products[products.category==category]
    if search: products=products[products.product_name.str.contains(search,case=False,na=False)|products.description.str.contains(search,case=False,na=False)]
    st.caption(f"{len(products)} products · Prices shown are catalogue starting monthly rates; eligibility depends on your saved profile.")
    for _,prod in products.iterrows():
        result=evaluate_product(prod,{**st.session_state.profile,"selected_ids":list(st.session_state.bundle.keys())})
        with st.container(border=True):
            left,right=st.columns([5,1]); left.markdown(f"#### {prod.product_name}  ·  `{prod.product_id}`"); left.write(prod.description); left.caption(f"{prod.category} · {prod.unit} · {int(prod.min_contract_months)} month minimum · {int(prod.typical_install_days)} typical install days")
            left.caption(f"{inr(prod.price_min_inr_per_month)}–{inr(prod.price_max_inr_per_month)} / month · setup {inr(prod.one_time_setup_inr)} · eligibility: {result['status']}")
            if result["reasons"] or result["missing"]: left.caption(" · ".join(result["reasons"]+result["missing"]))
            if right.button("Add",key=f"catalog_{prod.product_id}"):
                st.session_state.bundle[prod.product_id]=st.session_state.bundle.get(prod.product_id,0)+1; st.toast(f"{prod.product_name} added")

elif page=="Bundle Builder":
    heading("Build your bundle","Adjust quantities and see an indicative total calculated from catalogue starting rates.")
    if not st.session_state.bundle: st.info("Your bundle is empty. Add products from the catalogue or advisor.")
    quantities={}
    for pid,qty in list(st.session_state.bundle.items()):
        prod=catalogue[catalogue.product_id==pid].iloc[0]; a,b,c=st.columns([5,2,1]); a.write(f"**{prod.product_name}** · {prod.description}"); a.caption(f"{inr(prod.price_min_inr_per_month)} per {prod.unit} / month · setup {inr(prod.one_time_setup_inr)}")
        newqty=b.number_input(f"Quantity · {pid}",0,1000,int(qty),key=f"qty_{pid}")
        if c.button("Remove",key=f"remove_{pid}"): st.session_state.bundle.pop(pid); st.rerun()
        if newqty: quantities[pid]=newqty
    st.session_state.bundle=quantities
    quote=calculate_quote(catalogue,quantities,st.session_state.profile)
    a,b,c=st.columns(3); a.metric("Monthly estimate",inr(quote["monthly_total"])); b.metric("One-time setup",inr(quote["setup_total"])); c.metric("Minimum contract",f"{quote['contract_months']} months")
    if quote["install_days"]: st.caption(f"Longest catalogue installation estimate in this bundle: up to {quote['install_days']} days (product-specific typical estimate).")
    bundle_eligible=True
    for line in quote["items"]:
        prod=catalogue[catalogue.product_id==line["product_id"]].iloc[0]; el=evaluate_product(prod,{**st.session_state.profile,"selected_ids":list(quantities)})
        if el["status"]!="Eligible":
            bundle_eligible=False
            st.warning(f"{line['product_name']}: {el['status']}. " + "; ".join(el["reasons"]+el["missing"]))
    st.session_state.current_quote=quote
    if not bundle_eligible and quote["items"]: st.info("Resolve the eligibility items above before saving this quote.")
    if st.button("Review and save quote",type="primary",disabled=not quote["items"] or not bundle_eligible):
        if not st.session_state.profile.get("business_name"): st.error("Add a business name on Overview before saving a quote.")
        else:
            save_business(st.session_state.profile); qid=save_quote(st.session_state.profile["id"],quote); st.session_state.active_quote=qid; st.success(f"Quote {qid} saved. Review it in Quotes & Orders.")

elif page=="Quotes & Orders":
    heading("Quotes & orders","Review saved quotes and create a demo order after accepting a quote.")
    p=st.session_state.profile; quotes=list_quotes(p["id"])
    if not quotes: st.info("No quotes saved yet. Configure a bundle and select ‘Review and save quote’.")
    for q in quotes:
        data=json.loads(q["quote_json"]); st.markdown(f"#### {q['id']} · {q['status']} · {q['created_at']}")
        st.write(f"{len(data['items'])} line items · {inr(data['monthly_total'])}/month · setup {inr(data['setup_total'])}")
        current=calculate_quote(catalogue,st.session_state.bundle,p)
        changed=current != data
        if q["status"]=="Saved":
            if changed:
                st.warning("Your current bundle or catalogue pricing differs from this saved quote. Recalculate before accepting if you want the latest configuration.")
            if st.button(f"Recalculate {q['id']} from current bundle",key=f"recalc_{q['id']}",disabled=not st.session_state.bundle or not changed):
                checks=[evaluate_product(catalogue[catalogue.product_id==pid].iloc[0],{**p,"selected_ids":list(st.session_state.bundle)}) for pid in st.session_state.bundle]
                if any(c["status"]!="Eligible" for c in checks): st.error("The current bundle has unresolved eligibility requirements. Resolve them before recalculating this quote.")
                else:
                    revision=revise_quote(p["id"],q["id"],current); st.success(f"Quote updated to revision {revision}."); st.rerun()
        with st.expander("Quote details"):
            for item in data["items"]: st.write(f"{item['product_name']} × {item['quantity']} — {inr(item['monthly'])}/month + {inr(item['setup'])} setup")
            st.caption(f"Starting catalogue rates. No taxes, discounts, or external commercial terms are included. Contract minimum: {data['contract_months']} months.")
        quote_product_ids=[item["product_id"] for item in data.get("items",[])]
        quote_checks=[evaluate_product(catalogue[catalogue.product_id==pid].iloc[0],{**p,"selected_ids":quote_product_ids}) for pid in quote_product_ids if not catalogue[catalogue.product_id==pid].empty]
        quote_eligible=bool(quote_checks) and all(check["status"]=="Eligible" for check in quote_checks)
        if q["status"]=="Saved" and not quote_eligible: st.warning("Eligibility changed since this quote was saved. Update the profile or bundle and recalculate it.")
        if st.button(f"Accept {q['id']}",key=f"accept_{q['id']}",type="primary",disabled=q["status"]!="Saved" or changed or not quote_eligible):
            try:
                order=accept_quote_checked(p["id"],q["id"],catalogue,p); st.session_state.active_order=order; st.success(f"Demo order {order} created. Continue to Smart KYC."); st.rerun()
            except ValueError as exc: st.error(f"Quote needs attention before acceptance: {exc}")

elif page=="Smart KYC":
    heading("Smart KYC","Consent-first demo checks. Uploaded files are checked for type/size only; they are not saved, OCR processed, or treated as verification.")
    p=st.session_state.profile; order_id=st.session_state.active_order
    st.warning("Mock registry verification only. No government system is contacted. Do not upload real personal or business documents in this demo.")
    consent=st.checkbox("I consent to use the supplied mock registries for this demo verification purpose.",key="kyc_consent")
    if st.button("Record consent",type="primary"):
        record_registry_consent(p["id"],consent)
        st.session_state.consent=consent
        st.success("Consent recorded." if consent else "Consent withdrawal recorded.")
    if st.session_state.get("consent"):
        st.markdown("### Registry checks")
        st.caption("Synthetic sample certificates are only for exercising upload type checks. The app does not extract or verify their contents.")
        gst=st.text_input("GSTIN (optional)",max_chars=15,key="kyc_gstin")
        udyam=st.text_input("Udyam registration number (optional)",max_chars=19,key="kyc_udyam")
        gcol,ucol=st.columns(2)
        gcol.download_button("Download synthetic GST certificate",make_sample_pdf("GST registration sample",["Business: Balaji Dental Care LLP","GSTIN: 32TTNXB7384T1ZW","Registry: Mock dataset sample","Status: Active (mock only)"]),"synthetic_gst_sample.pdf","application/pdf",key="sample_gst")
        ucol.download_button("Download synthetic Udyam certificate",make_sample_pdf("Udyam registration sample",["Enterprise: Balaji Dental Care LLP","Udyam number: UDYAM-KL-00-3078801","Enterprise type: Micro","Registry: Mock dataset sample"]),"synthetic_udyam_sample.pdf","application/pdf",key="sample_udyam")
        upload=st.file_uploader("Optional synthetic specimen file (PDF, PNG, JPEG; max 5 MB)",type=["pdf","png","jpg","jpeg"],max_upload_size=MAX_UPLOAD_BYTES//(1024*1024))
        upload_ok=True
        if upload:
            accepted,message=validate_specimen_upload(upload.name,upload.getvalue(),MAX_UPLOAD_BYTES)
            if not accepted: upload_ok=False; st.error(message)
            else: st.success(message)
        if st.button("Run demo checks",disabled=not upload_ok):
            if not registry_consent_granted(p["id"]):
                st.error("Consent is not currently active. Record consent again before checking registry data.")
                st.stop()
            results=[]
            if gst:
                g=verify_gstin(gst); results.append({"check":"GSTIN format and checksum","status":"Passed" if g["format_valid"] else "Failed","detail":g["message"]})
                results.append({"check":"Mock GSTIN registry","status":g["status"],"detail":g["message"]})
                if g.get("record"):
                    if p.get("business_name") and p["business_name"].casefold() not in str(g["record"].get("trade_name","")).casefold(): results.append({"check":"Business name comparison","status":"Warning","detail":"Provided name does not closely match the mock registry trade name."})
                    state_match=not p.get("state") or p["state"].casefold()==str(g["record"].get("state","")).casefold()
                    results.append({"check":"GSTIN state consistency","status":"Passed" if state_match else "Warning","detail":"Business state matches the mock record." if state_match else "Business state differs from the mock registry record."})
            if udyam:
                u=verify_udyam(udyam); results.append({"check":"Udyam format","status":"Passed" if u["format_valid"] else "Failed","detail":u["message"]}); results.append({"check":"Mock Udyam registry","status":u["status"],"detail":u["message"]})
                if u.get("record"):
                    if p.get("business_name") and p["business_name"].casefold() not in str(u["record"].get("enterprise_name","")).casefold(): results.append({"check":"Enterprise name comparison","status":"Warning","detail":"Provided name does not closely match the mock registry enterprise name."})
                    state_match=not p.get("state") or p["state"].casefold()==str(u["record"].get("state","")).casefold()
                    results.append({"check":"Udyam state consistency","status":"Passed" if state_match else "Warning","detail":"Business state matches the mock record." if state_match else "Business state differs from the mock registry record."})
            if not gst and not udyam: results.append({"check":"Identifiers","status":"Requires action","detail":"Enter a GSTIN or Udyam number to run a registry check."})
            save_kyc_result(p["id"],results); st.session_state.kyc_results=results
            if order_id:
                try:
                    passed=bool(results) and all(r["status"] in ("Passed","Active","Matched in mock registry") for r in results)
                    outcome=record_kyc_outcome(order_id,passed)
                    if outcome["message"].startswith("KYC cannot change"): st.warning(outcome["message"])
                except ValueError as exc: st.error(f"Could not update the demo order: {exc}")
            st.rerun()
        for row in st.session_state.get("kyc_results",[]):
            st.markdown(f"**{row['check']} — {row['status']}**  \n{row['detail']}")
    else: st.info("Record consent before running any registry check.")

elif page=="Order Tracker":
    heading("Order tracker","Follow status changes recorded in this demo. No live Airtel fulfilment connection exists.")
    oid=st.text_input("Order reference",value=st.session_state.active_order or "",placeholder="UO-XXXXXXXX")
    if st.button("Track order"):
        order=get_order(oid.strip())
        if order: st.session_state.tracked_order=order
        else: st.error("No demo order found for that reference.")
    order=st.session_state.get("tracked_order")
    if order:
        st.markdown(f"### {order['id']} · {order['status']}")
        st.caption("SIMULATED DEMO STATUS · Not connected to Airtel systems")
        lifecycle=["KYC Pending","KYC In Progress","KYC Action Required","KYC Verified","Order Processing","Installation Scheduled","Installation In Progress","Activated"]
        progress=max(0,lifecycle.index(order["status"]) if order["status"] in lifecycle else 0)
        st.progress(progress/max(1,len(lifecycle)-1),text="Demo onboarding progress")
        st.write("Selected services:",", ".join(i["product_name"] for i in order["quote"]["items"]))
        for ev in order["events"]: st.markdown(f"**{ev['status']}** · {ev['created_at']}  \n{ev['note']}")
        status=order["status"]
        if status=="KYC Verified":
            if st.button("Move demo order to processing",type="primary"):
                advance_order(order["id"],"Order Processing","Simulated demo order processing started.")
        elif status=="Order Processing":
            if st.button("Schedule demo installation",type="primary"): advance_order(order["id"],"Installation Scheduled","Simulated installation slot scheduled.")
        elif status=="Installation Scheduled":
            if st.button("Start demo installation",type="primary"): advance_order(order["id"],"Installation In Progress","Simulated installation work started.")
        elif status=="Installation In Progress":
            if st.button("Mark demo journey complete",type="primary"): advance_order(order["id"],"Activated","Demo journey marked complete; this does not indicate real service activation.")

elif page=="Operations Dashboard":
    heading("Operations dashboard","Synthetic demonstration metrics only. These generated records contain no real lead-level business data and are not live operational data.")
    df=load_analytics()
    if df.empty: st.info("The synthetic demo analytics file is missing. Restore data/analytics/synthetic_demo_leads.csv from the repository or regenerate it with scripts/generate_synthetic_analytics.py.")
    else:
        all_activated=df[df.outcome=="Activated"]
        micro=df[df.segment=="Micro retail & services"]
        with st.expander("Synthetic demo baseline",expanded=False):
            gst_rates=df.groupby("has_gstin").apply(lambda x:(x.outcome=="Activated").mean(),include_groups=False)
            st.write(f"{len(df):,} leads · {len(all_activated):,} activations ({len(all_activated)/len(df):.2%}) · {all_activated.days_lead_to_activation.mean():.2f} mean days to activation · {(all_activated.churned_within_6_months=='Y').sum():,} churned activations.")
            st.write(f"Micro retail & services: {len(micro)/len(df):.1%} of leads, {(micro.outcome=='Activated').mean():.1%} activated. GSTIN present: {gst_rates.get('Y',0):.1%} activated; absent: {gst_rates.get('N',0):.1%} activated.")
            st.caption("The CSV does not contain a direct requested-product ineligibility outcome field, so an ineligibility percentage is not presented as an observed case-study metric.")
        seg=st.multiselect("Business segment",sorted(df.segment.dropna().unique()),default=sorted(df.segment.dropna().unique())); tier=st.multiselect("City tier",sorted(df.city_tier.dropna().unique()),default=sorted(df.city_tier.dropna().unique()))
        data=df[df.segment.isin(seg)&df.city_tier.isin(tier)]; total=len(data); activated=int((data.outcome=="Activated").sum()); avg=pd.to_numeric(data.days_lead_to_activation,errors="coerce").mean(); churn=int(((data.outcome=="Activated")&(data.churned_within_6_months=="Y")).sum())
        a,b,c,d=st.columns(4); a.metric("Leads",f"{total:,}"); b.metric("Activated",f"{activated:,}"); c.metric("Activation rate",f"{activated/total:.2%}" if total else "—"); d.metric("Avg. lead to activation",f"{avg:.1f} days" if pd.notna(avg) else "—")
        e,f,g,h=st.columns(4); e.metric("Churned within 6 months",f"{churn:,}"); f.metric("KYC complete",f"{(data.stage_reached=='KYC complete').sum():,}"); g.metric("Leads with GSTIN",f"{(data.has_gstin=='Y').sum():,}"); h.metric("Non-activated",f"{total-activated:,}")
        left,right=st.columns(2)
        stage=data.groupby("stage_reached",dropna=False).size().reset_index(name="Leads"); left.plotly_chart(px.funnel(stage,x="Leads",y="stage_reached",title="Lead stage distribution"),width="stretch")
        conv=data.groupby("segment").apply(lambda x:(x.outcome=="Activated").mean(),include_groups=False).reset_index(name="Activation rate"); right.plotly_chart(px.bar(conv,x="segment",y="Activation rate",title="Activation by segment",text_auto=".1%"),width="stretch")
        left,right=st.columns(2)
        gst=data.groupby("has_gstin").apply(lambda x:(x.outcome=="Activated").mean(),include_groups=False).reset_index(name="Activation rate"); left.plotly_chart(px.bar(gst,x="has_gstin",y="Activation rate",title="GSTIN availability and activation",text_auto=".1%"),width="stretch")
        reasons=data[data.outcome!="Activated"].dropna(subset=["drop_reason"]).groupby("drop_reason").size().sort_values(ascending=False).head(10).reset_index(name="Leads"); right.plotly_chart(px.bar(reasons,x="Leads",y="drop_reason",orientation="h",title="Most common recorded drop reasons"),width="stretch")
        st.markdown("### Data-grounded observations")
        if not conv.empty:
            lowest=conv.sort_values("Activation rate").iloc[0]; st.write(f"• Lowest conversion in the selected data: **{lowest['segment']}** at {lowest['Activation rate']:.1%}.")
        if not reasons.empty: st.write(f"• Most common recorded non-activation reason: **{reasons.iloc[0]['drop_reason']}** ({int(reasons.iloc[0]['Leads'])} leads in the filtered data).")
        st.caption("Synthetic demo records only; no real lead-level data is included. Segment and city-tier filters apply to every displayed metric.")

else:
    heading("Settings","Demo workspace preferences and environment status.")
    st.write("Language preference",lang); st.write("Application data store","Local SQLite demo database"); st.write("LLM/OCR/payment/Airtel integrations","Not configured; deterministic demo paths remain available.")
    st.caption("For durable production use, configure managed database storage and real integration adapters before handling real customer records.")
