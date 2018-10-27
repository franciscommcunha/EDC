from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
import datetime
import requests
import os
from lxml import etree

from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import json

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

from bills import rules

"""
Sites visited for this project:
    https://www.tutorialspoint.com/python/python_xml_processing.html
"""

# Renders the home page and converts the original XML file to the RDF file
def index(request):
    xml = get_weather()

    return render(
        request,
        "index.html",
        {
           "xml": xml,
        })

# generate new triples based on client postal-code and telephone number
def apply_inference():
    # dictionary containing the rule
    rule = rules.pc_rule
    # get client entity and respective postal-code
    q_str = """ 
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select distinct ?v
            where{
                ?sub ns0:client_pc ?v
            }
            """
    result = query(q_str)
    result = result['results']['bindings']

    for r in result:
        value = r['v']['value']
        # for each pair of client,postal-code apply insert
        for pc in rule.keys():
            if int(value.split("-")[0]) >= pc[0] and int(value.split("-")[0]) <= pc[1]:
                region = rule[pc]

                q_region = """
                        prefix ns0: <http://xmlns.com/foaf/spec/>
                        select distinct ?o
                        where {
                            ?s ns0:client_pc '"""+value+"""'.
                            ?s ns0:client_region ?o.
                        }
                        """
                res = query(q_region)
                try:
                    reg = res['results']['bindings'][0]['o']['value']
                    region = reg.split()[0].replace(",", "") + ", " + region
                except Exception:
                    reg = ""

                qstr = """ 
                        prefix ns0: <http://xmlns.com/foaf/spec/>
                        delete {?sub ns0:client_region '"""+reg+"""'}
                        where {?sub ns0:client_pc '"""+value+"""'};
                        insert {?sub ns0:client_region '"""+region+"""'}
                        where {?sub ns0:client_pc '"""+value+"""'}
                        """
                print(qstr)
                query(qstr)
                            
    return

def apply_inference2():
    ## apply telephone rules
    # dictionary containing the rule
    p_rule = rules.phone_rule 

    # get client entity and respective postal-code
    q_str = """ 
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?v
            where{
                ?sub ns0:ClientContact ?obj.
                ?obj ns0:client_tel ?v
            }
            """

    result = query(q_str)  
    result = result['results']['bindings']

    for r in result:
        value = r['v']['value']
        # for each pair of client,phone number apply insert
        if(value==""):
            continue
        for pc in p_rule.keys():
            # if number indicative matches rule then insert region
            if(int(value[0:3])==pc):
                region = p_rule[pc]         

                q_region = """
                        PREFIX ns0: <http://xmlns.com/foaf/spec/>
                        select distinct ?v
                        where {
                            ?s a ns0:ClientContact.
                            ?s ns0:client_tel '"""+value+"""'.
                            optional {?sub ns0:ClientContact ?s. ?sub ns0:ClientAddress ?o. ?o ns0:client_region ?v}
                        }
                        """
                res = query(q_region)
                
                try:
                    reg = res['results']['bindings'][0]['v']['value']
                    region = reg.split()[0].replace(",", "") + ", " + region
                except Exception:
                    reg = ""

                qstr = """ 
                        prefix ns0: <http://xmlns.com/foaf/spec/>
                        insert {?sub ns0:client_region '"""+region+"""'.}
                        where {?sub ns0:client_tel '"""+str(value)+"""'.};
                        delete {?sub ns0:client_region '"""+reg+"""'.}
                        where {?sub ns0:client_tel '"""+str(value)+"""'.};
                        """
                query(q_str)
                #print(qstr)
    return

# Replaces the client's information with new information
def save_product_info(request):
    p_id = request.POST.get("ProductID")
    price = request.POST.get("Price")
    name = request.POST.get("Name")
    tax_desc = request.POST.get("TaxDescription")

    q_tax = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?s
            where{
                ?s ns0:tax_desc '"""+tax_desc+"""'.
            }
            """

    result = query(q_tax)
    tax = result['results']['bindings'][0]['s']['value'][36:]
    print(tax)

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            prefix product: <http://www.padaria.com/products/>
            prefix tax: <http://www.padaria.com/products/tax/>
            delete {product:"""+p_id+""" ns0:prod_name ?o.}
            where {product:"""+p_id+""" ns0:prod_name ?o.};
            delete {product:"""+p_id+""" ns0:cost ?o.}
            where {product:"""+p_id+""" ns0:cost ?o.};
            delete {tax:"""+p_id+""" ns0:desc ?o.}
            where {tax:"""+p_id+""" ns0:desc ?o.};
            insert data {
                product:"""+p_id+""" ns0:prod_name '"""+name+"""'.
                product:"""+p_id+""" ns0:cost '"""+price+"""'.
                tax:"""+p_id+""" ns0:desc tax:"""+tax+""".
            }
            """
    print(q_str)
    query(q_str)
    return info_products(request, name)

# Receives the stored product's data to display in the edit page
def edit_product_info(request):
    product_info = request.POST.get("product_info")
    product_name = request.POST.get("product_name")
    product_info = product_info.replace("[", "").replace("]", "").replace("\'", "").split(",")

    p_info = {}
    p_info["name"] = product_name.lstrip()
    p_info["ProductID"] = product_info[0].lstrip().replace("(", "")
    p_info["Price"] = product_info[1].lstrip()
    p_info["TaxType"] = product_info[2].lstrip()
    p_info["TaxDescription"] = product_info[3].lstrip()
    p_info["TaxValue"] = product_info[4].lstrip().replace(")", "")

    return render(request, "edit_product_info.html", p_info)

# Replaces the client's information with new information
def save_client_info(request):

    c_id = request.POST.get("ID")
    name = request.POST.get("Name")
    address = request.POST.get("Address")
    city = request.POST.get("City")
    postal = request.POST.get("PostalCode")
    region = request.POST.get("Region")
    country = request.POST.get("Country")
    tel = request.POST.get("Telephone")
    fax = request.POST.get("Fax")
    email = request.POST.get("Email")

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            prefix client: <http://www.padaria.com/clients/>
            prefix client_addr: <http://www.padaria.com/clients/client_address/>
            prefix client_cont: <http://www.padaria.com/clients/client_contact/>
            delete {client:"""+c_id+""" ns0:client_name ?o.}
            where {client:"""+c_id+""" ns0:client_name ?o.};
            delete {client_addr:"""+c_id+""" ns0:client_address ?o.}
            where {client_addr:"""+c_id+""" ns0:client_address ?o.};
            delete {client_addr:"""+c_id+""" ns0:client_city ?o.}
            where {client_addr:"""+c_id+""" ns0:client_city ?o.};
            delete {client_addr:"""+c_id+""" ns0:client_pc ?o.}
            where {client_addr:"""+c_id+""" ns0:client_pc ?o.};
            delete {client_addr:"""+c_id+""" ns0:client_region ?o.}
            where {client_addr:"""+c_id+""" ns0:client_region ?o.};
            delete {client_addr:"""+c_id+""" ns0:client_country ?o.}
            where {client_addr:"""+c_id+""" ns0:client_country ?o.};
            delete {client_cont:"""+c_id+""" ns0:client_tel ?o.}
            where {client_cont:"""+c_id+""" ns0:client_tel ?o.};
            delete {client_cont:"""+c_id+""" ns0:client_tax ?o.}
            where {client_cont:"""+c_id+""" ns0:client_tax ?o.};
            delete {client_cont:"""+c_id+""" ns0:client_mail ?o.}
            where {client_cont:"""+c_id+""" ns0:client_mail ?o.};
            insert data {
                client:"""+c_id+""" ns0:client_name '"""+name+"""'.
                client_addr:"""+c_id+""" ns0:client_address '"""+address+"""'.
                client_addr:"""+c_id+""" ns0:client_city '"""+city+"""'.
                client_addr:"""+c_id+""" ns0:client_pc '"""+postal+"""'.
                client_addr:"""+c_id+""" ns0:client_region '"""+region+"""'.
                client_addr:"""+c_id+""" ns0:client_country '"""+country+"""'.
                client_cont:"""+c_id+""" ns0:client_tel '"""+tel+"""'.
                client_cont:"""+c_id+""" ns0:client_tax '"""+fax+"""'.
                client_cont:"""+c_id+""" ns0:client_mail '"""+email+"""'.
            }
            """

    query(q_str)
    apply_inference()
    return clients_info(request, name)

# Receives the stored client's data to display in the edit page
def edit_client_info(request):

    client_info = request.POST.get("client_info")

    client_name = request.POST.get("client_name")

    client_info = client_info.replace("[", "").replace("]", "").replace("\'", "").split(",")
    c_info = {}

    print(len(client_info))
    if len(client_info) > 10:
        c_info["ID"] = client_info[0].replace("(", "")
        c_info["Address"] = client_info[2].lstrip()
        c_info["City"] = client_info[3].lstrip()
        c_info["PostalCode"] = client_info[4].lstrip()
        c_info["Region"] = client_info[5].lstrip() + ", " + client_info[6].lstrip()
        c_info["Country"] = client_info[7].lstrip()
        c_info["Telephone"] = client_info[8].lstrip()
        c_info["Fax"] = client_info[9].lstrip()
        c_info["Email"] = client_info[10].lstrip().replace(")", "")
        c_info["Name"] = client_name
    else:
        c_info["ID"] = client_info[0].replace("(", "")
        c_info["Address"] = client_info[2].lstrip()
        c_info["City"] = client_info[3].lstrip()
        c_info["PostalCode"] = client_info[4].lstrip()
        c_info["Region"] = client_info[5].lstrip()
        c_info["Country"] = client_info[6].lstrip()
        c_info["Telephone"] = client_info[7].lstrip()
        c_info["Fax"] = client_info[8].lstrip()
        c_info["Email"] = client_info[9].lstrip().replace(")", "")
        c_info["Name"] = client_name

    return render(request, "edit_client_info.html", c_info)

# Searches for the given string and orders the search results
def search(request):

    obj = request.POST.get("input") if request.GET.get('search') is None else request.GET.get('search')
    sort = request.POST.get("selected")

    q_prod_client = """
                prefix ns0: <http://xmlns.com/foaf/spec/>
                select distinct ?s ?o
                where{
                    {
                        ?s ns0:prod_name ?o.
                        filter regex(?o,'"""+obj+"""','i')
                    }
                    union
                    {
                        ?s ns0:client_name ?o.
                        filter regex(?o,'"""+obj+"""','i')
                    }
                }
                """

    q_trans = """
                prefix ns0: <http://xmlns.com/foaf/spec/>
                select ?sub ?val ?obj
                where{
                    {
                        ?sub ?p ns0:Transaction.
                        ?sub ns0:trans_client ?v.
                        optional{?v ns0:client_name ?val}
                        ?sub ns0:trans_prod ?o.
                        optional{?o ns0:prod_name ?obj}
                        filter regex(?val,'"""+obj+"""','i')
                    }
                    union
                    {
                        ?sub ?p ns0:Transaction.
                        ?sub ns0:trans_client ?v.
                        optional{?v ns0:client_name ?val}
                        ?sub ns0:trans_prod ?o.
                        optional{?o ns0:prod_name ?obj}
                        filter regex(?obj,'"""+obj+"""','i')
                    }
                }
                """

    result_pc = query(q_prod_client)
    result_t = query(q_trans)

    results = {}
    results_prod = {}
    results_client = {}
    results_tran = {}

    results["input"] = obj
    results["value_sort"] = "default" if sort is None else sort


    for element in result_pc['results']['bindings']:
        if "products" in element['s']['value']:
            results_prod[element['s']['value'][-2:]] = []

    for element in result_pc['results']['bindings']:
        if "products" in element['s']['value'] and element['o']['type'] != 'uri':
            results_prod[element['s']['value'][-2:]].append(element['o']['value'])


    for element in result_pc['results']['bindings']:
        if "clients" in element['s']['value']:
            results_client[element['s']['value'][-2:]] = []

    for element in result_pc['results']['bindings']:
        if "clients" in element['s']['value'] and element['o']['type'] != 'uri':
            results_client[element['s']['value'][-2:]].append(element['o']['value'])


    for element in result_t['results']['bindings']:
        results_tran[element['sub']['value'][-2:]] = []

    for element in result_t['results']['bindings']:
        results_tran[element['sub']['value'][-2:]].append(element['obj']['value'])
        results_tran[element['sub']['value'][-2:]].append(element['val']['value'])

    results["products"] = sorted(results_prod.values())
    results["clients"] = sorted(results_client.values())
    results["transactions"] = sorted(results_tran.values())

    if results["value_sort"] == "z-a":
        results["order"] = sorted(results["products"]+results["clients"]+results["transactions"], reverse=True)
    else:
        results["order"] = sorted(results["products"]+results["clients"]+results["transactions"])

    results["count"] = len(results["clients"]) + len(results["products"]) + len(results["transactions"])
    results["search_flag"] = True

    xml = get_weather()

    results["xml"] = xml

    return render(
        request,
        "index.html",
        results,
    )

# Adds a client to the database
def add_client(request):

    if "name" in request.POST and "address" in request.POST and "city" in request.POST and "postal" in request.POST and \
                    "region" in request.POST and "country" in request.POST and "tel" in request.POST and \
                    "fax" in request.POST and "email" in request.POST:

        name = request.POST["name"]
        address = request.POST["address"]
        city = request.POST["city"]
        postal = request.POST["postal"]
        region = request.POST["region"]
        country = request.POST["country"]
        tel = request.POST["tel"]
        fax = request.POST["fax"]
        email = request.POST["email"]

        if name and address and postal and email:

            q_max = """
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    select ?s
                    where {?s a ns0:Clients}
                    order by desc(?s) limit 1  
                      """

            result = query(q_max)
            id = str(int(result['results']['bindings'][0]['s']['value'][-2:]) + 1)

            q_str = """
                    prefix client: <http://www.padaria.com/clients/>
                    prefix client_addr: <http://www.padaria.com/clients/client_address/>
                    prefix client_cont: <http://www.padaria.com/clients/client_contact/>
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    insert DATA
                    {
                        client:"""+id+""" a ns0:Clients.
                        client:"""+id+""" ns0:client_name '"""+name+"""'.
                        client:"""+id+""" ns0:ClientAddress client_addr:"""+id+""".
                        client:"""+id+""" ns0:ClientContact client_cont:"""+id+""".
                        client_addr:"""+id+""" a ns0:ClientAddress.
                        client_addr:"""+id+""" ns0:client_address '"""+address+"""'.
                        client_addr:"""+id+""" ns0:client_city '"""+city+"""' .
                        client_addr:"""+id+""" ns0:client_pc '"""+postal+"""' .
                        client_addr:"""+id+""" ns0:client_region '"""+region+"""' .
                        client_addr:"""+id+""" ns0:client_country '"""+country+"""' .
                        client_cont:"""+id+""" a ns0:ClientContact .
                        client_cont:"""+id+""" ns0:client_tel '"""+tel+"""' .
                        client_cont:"""+id+""" ns0:client_fax '"""+fax+"""'.
                        client_cont:"""+id+""" ns0:client_mail '"""+email+"""'.
                    }
                    """

            query(q_str)
            apply_inference()

            return render(
                request,
                "add_client.html",
                {
                    "error": False,
                })
        else:
            return render(
                request,
                "add_client.html",
                {
                    "error": True,
                })
    else:
        return render(
            request,
            "add_client.html",
            {
                "error": None,
            })

# Adds a product to the database
def add_product(request):

    if "name" in request.POST and "cost" in request.POST and "type" in request.POST and "description" in request.POST:
        name = request.POST["name"]
        cost = request.POST["cost"]
        type = request.POST["type"]
        description = request.POST["description"]

        if name and cost and type and description:
            q_max = """
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    select ?s
                    where {?s a ns0:Product}
                    order by desc(?s) limit 1  
                    """

            result = query(q_max)
            id = str(int(result['results']['bindings'][0]['s']['value'][-2:]) + 1)

            q_desc = """
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    select ?s
                    where {?s ?p "Taxa Normal"}
                    """
            result = query(q_desc)
            desc = result['results']['bindings'][0]['s']['value'][36:]

            q_str = '''
                    prefix product: <http://www.padaria.com/products/>
                    prefix tax: <http://www.padaria.com/products/tax/>
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    insert DATA
                    {
                        product:''' + id + ''' a ns0:Product.
                        product:''' + id + ''' ns0:prod_name "''' + name + '''".
                        product:''' + id + ''' ns0:cost "''' + cost + '''".
                        product:''' + id + ''' ns0:Tax tax:''' + id + '''.
                        tax:''' + id + ''' a ns0:Tax.
                        tax:''' + id + ''' ns0:t_type "''' + type + '''".
                        tax:''' + id + ''' ns0:desc tax:''' + desc + '''.
                    }
                    '''

            query(q_str)

            return render(
                request,
                "add_product.html",
                {
                    "error": False,
                })
        else:
            return render(
                request,
                "add_product.html",
                {
                    "error": True,
                })
    else:
        return render(
            request,
            "add_product.html",
            {
                "error": None,
            })

# Adds a sale to the database
def add_sale(request):

    if "client_id" in request.POST and "prod_id" in request.POST and "quant" in request.POST:

        client_id = request.POST["client_id"] if int(request.POST["client_id"]) > 10 else '0'+request.POST["client_id"]
        prod_id = request.POST["prod_id"] if int(request.POST["prod_id"]) > 10 else '0'+request.POST["prod_id"]
        quant = request.POST["quant"]

        if client_id and prod_id and quant:

            q_max = """
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    select ?s
                    where {?s a ns0:Transaction}
                    order by desc(?s) limit 1
                    """

            result = query(q_max)
            id = str(int(result['results']['bindings'][0]['s']['value'][-2:]) + 1)

            q_price = """
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    prefix product: <http://www.padaria.com/products/>
                    select ?o
                    where {product:"""+prod_id+""" ns0:cost ?o}
                    """

            result = query(q_price)
            price = result['results']['bindings'][0]['o']['value']

            q_str = """
                    prefix ns0: <http://xmlns.com/foaf/spec/>
                    prefix client_trans: <http://www.padaria.com/clients/transactions/>
                    prefix trans_time: <http://www.padaria.com/clients/transactions/transaction_time/>
                    prefix client: <http://www.padaria.com/clients/>
                    prefix product: <http://www.padaria.com/products/>
                    insert DATA{
                        client_trans:"""+id+""" a ns0:Transaction.
                        client_trans:"""+id+""" ns0:trans_client client:"""+client_id+""".
                        client_trans:"""+id+""" ns0:trans_prod product:"""+prod_id+""".
                        client_trans:"""+id+""" ns0:trans_prod_quant '"""+quant+"""'.
                        client_trans:"""+id+""" ns0:trans_total_cost '"""+str(round(int(quant)*float(price),2))+"""'.
                        client_trans:"""+id+""" ns0:TransactionTime trans_time:"""+id+""".
                        trans_time:"""+id+""" a ns0:TransactionTime.
                        trans_time:"""+id+""" ns0:trans_date '"""+datetime.datetime.now().strftime("%Y-%m-%d")+"""'.
                        trans_time:"""+id+""" ns0:trans_time '"""+datetime.datetime.now().strftime("%H:%M")+"""'.
                    }
                   """

            query(q_str)

            return render(
                request,
                'add_sale.html',
                {
                    "error": False,
                }
            )

        else:

            return render(
                request,
                'add_sale.html',
                {
                    "error": True,
                }
            )

    else:
        return render(
            request,
            'add_sale.html',
            {
                "error": None,
            }
        )

# Lists all the products
def list_products(request):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?o ?v
            where{
                ?sub ?p ns0:Product.
                ?sub ?pred ?o.
                optional {?o ?predicado ?v}
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value'][-2:]] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [element['v']['value']]

    return render(
        request,
        "list_products.html",
        {
            "products": sorted(results.items()),
        })

# Displays info about a product
def info_products(request, name):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?o ?v
            where{
                {
                    ?sub ns0:prod_name ?obj.
                    ?sub ns0:cost ?o.
                    filter (?obj = '"""+name+"""')
                }
                union
                {
                    ?sub ns0:prod_name ?obj.
                    ?sub ns0:Tax ?ob.
                    ?ob ?p ?o.
                    optional {?o ?pred ?v}
                    filter (?obj = '"""+name+"""')
                }
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value'][-2:]] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [element['v']['value']]

    return render(
        request,
        "info_products.html",
        {
            "products": sorted(results.items())[0],
            "name": name,
        }
    )

# Lists all the clients
def list_clients(request):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?o ?v
            where{
                ?sub ?p ns0:Clients.
                ?sub ?pred ?o.
                optional {?o ?predicado ?v}
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value'][-2:]] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [element['v']['value']]

    return render(
        request,
        "list_clients.html",
        {
            "customers": sorted(results.items()),
        })

#  Given a client, shows its info
def clients_info(request, name):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?o ?v
            where{
                ?sub ns0:client_name ?obj.
                ?sub ?p ?o
                filter (?obj = '"""+name+"""')
                optional {?o ?pred ?v}
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value'][-2:]] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [element['v']['value']]

    return render(
        request,
        'info_clients.html',
        {
            'customers': sorted(results.items())[0],
            'name': name
        }
    )

# List all the taxes
def list_taxes(request):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select distinct ?sub ?o ?v
            where{
                {
                    ?s ?p ns0:Tax.
                    ?s ns0:t_type ?o.
                    ?s ns0:desc ?sub.
                    optional {
                        ?sub ?predicado ?v. 
                    }
                }
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value']] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value']] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value']] += [element['o']['value']]
                results[element['sub']['value']] += [element['v']['value']]

    return render(
        request,
        'list_taxes.html',
        {
            'taxes': sorted(results.items()),
        }
    )

# Given a tax shows it's products
def info_tax(request, name):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select distinct ?sub ?o
            where{
                ?subject ns0:tax_desc ?n.
                ?s ns0:desc ?subject.
                ?sub ?p ?s.
                ?sub ns0:prod_name ?o.
                filter(?n = '"""+name+"""')
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value']] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value']] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value']] += [element['v']['value']]

    return render(
        request,
        'info_tax.html',
        {
            'taxes': sorted(results.items()),
            'name': name,
        }
    )

# Shows all made sales
def list_sales(request):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?o ?v
            where{
                {
                    ?sub ?p ns0:Transaction.
                    ?sub ?pred ?o.
                    optional { ?o ?predicado ?v }
                }
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value'][-2:]] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [element['v']['value']]

    return render(
        request,
        'list_sales.html',
        {
            'sales': sorted(results.items()),
        }
    )

# Given a client's name, show the sales he made
def info_sales(request, name):

    q_str = """
            prefix ns0: <http://xmlns.com/foaf/spec/>
            select ?sub ?o ?v
            where{
                    ?s ns0:client_name ?obj.
                    ?sub ?pred ?s.
                    ?sub ?p ?o.
                    optional { ?o ?predicado ?v }.
                    filter(?obj = '"""+name+"""').
            }
            """

    result = query(q_str)
    results = {}

    for element in result['results']['bindings']:
        results[element['sub']['value'][-2:]] = []

    for element in result['results']['bindings']:
        if len(element) == 2:
            if element['o']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [(element['o']['value'])]
        else:
            if element['o']['type'] != 'uri' or element['v']['type'] != 'uri':
                results[element['sub']['value'][-2:]] += [element['v']['value']]

    return render(
        request,
        'info_sales.html',
        {
            'sales': sorted(results.items()),
            'name': name,
        }
    )

# Retrieves the wikidata's inforation about Ovar
def ovar_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery(""" SELECT ?item ?itemLabel WHERE {
                        wd:Q404261 ?pred ?item.
            
                        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                            filter (?pred = wdt:P1082 || ?pred = wdt:P571 || ?pred = wdt:P17 || ?pred = wdt:P131 
                                    || ?pred = wdt:P625 || ?pred = wdt:P2046 || ?pred = wdt:P421 || ?pred = wdt:P281 
                                    || ?pred = wdt:P856 || ?pred = wdt:P18)
                        }
                    """)

    value = sparql_query(sparql)

    return render(
        request,
        'ovar_info.html',
        {
            'value': value,
            'name': "Ovar"
        }
    )

# Retrieves the wikidata's inforation about Válega
def valega_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery(""" SELECT ?item ?itemLabel WHERE {
                      wd:Q1867212 ?pred ?item.
                
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                      filter (?pred = wdt:P17 || ?pred = wdt:P131 || ?pred = wdt:P625
                              || ?pred = wdt:P2046 || ?pred = wdt:P18)
                    }
                
                    """)

    value = sparql_query(sparql)

    return render(
        request,
        'valega_info.html',
        {
            'value': value,
            'name': "Válega"
        }
    )

# Retrieves the wikidata's inforation about Pão
def pao_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery(""" SELECT ?item ?itemLabel WHERE {
                      wd:Q7802 ?pred ?item.
            
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                      filter (?pred = wdt:P31 || ?pred = wdt:P279 || ?pred = wdt:P18
                              || ?pred = wdt:P495 || ?pred = wdt:P186 || ?pred = wdt:P487)
                    }
                """)

    value = sparql_query(sparql)

    return render(
        request,
        'pao_info.html',
        {
            'value': value,
            'name': "Pão"
        }
    )

# Retrieves the wikidata's inforation about Croissant
def croissant_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery(""" 
                    SELECT ?item ?itemLabel WHERE {
                      wd:Q207832 ?pred ?item.
                    
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                      filter (?pred = wdt:P18 || ?pred = wdt:P495 || ?pred = wdt:P1419
                               || ?pred = wdt:P487)
                    }
            
                """)
    value = sparql_query(sparql)

    return render(
        request,
        'croissant_info.html',
        {
            'value': value,
            'name': "Croissant"
        }
    )

# Retrieves the wikidata's inforation about Broa
def broa_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery(""" SELECT ?item ?itemLabel WHERE {
                          wd:Q2642060 ?pred ?item.
                        
                          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                          filter (?pred = wdt:P31 || ?pred = wdt:P279 || ?pred = wdt:P18
                                  || ?pred = wdt:P495 || ?pred = wdt:P186)
                        
                            }                
                    """)

    value = sparql_query(sparql)

    return render(
        request,
        'broa_info.html',
        {
            'value': value,
            'name': "Broa de Milho"
        }
    )

# Retrieves the wikidata's inforation about Bolo Rei
def bolo_rei_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = sparql.setQuery(""" SELECT ?item ?itemLabel WHERE {
                              wd:Q177166 ?pred ?item.
                        
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                              filter (?pred = wdt:P18 || ?pred = wdt:P495 || ?pred = wdt:P31 || ?pred = wdt:P279)
                            }	
                            """)

    value = sparql_query(sparql)

    return render(
        request,
        'bolo_rei_info.html',
        {
            'value': value,
            'name': "Bolo-Rei"
        }
    )

# Retrieves the wikidata's inforation about Pão de Forma
def pao_de_forma_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = sparql.setQuery("""
                            SELECT ?item ?itemLabel WHERE {
                              wd:Q134152 ?pred ?item.
                            
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                              filter (?pred = wdt:P495 || ?pred = wdt:P18 || ?pred = wdt:P31)
                            }
                        """)

    value = sparql_query(sparql)

    return render(
        request,
        'pao_de_forma_info.html',
        {
            'value': value,
            'name': "Pão de Forma"
        }
    )

# Retrieves the wikidata's inforation about Pão de Ló
def pao_de_lo_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = sparql.setQuery("""
                            SELECT ?item ?itemLabel WHERE {
                              wd:Q1049852 ?pred ?item.
                            
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                              filter (?pred = wdt:P279 || ?pred = wdt:P18 || ?pred = wdt:P495 || ?pred = wdt:P373 || ?pred = wdt:P527)
                            }
                        """)

    value = sparql_query(sparql)

    return render(
        request,
        'pao_de_lo_info.html',
        {
            'value': value,
            'name': "Pão de Ló"
        }
    )

# Retrieves the wikidata's inforation about Pão de Mistura
def pao_de_mistura_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = sparql.setQuery("""
                            SELECT ?item ?itemLabel WHERE {
                              wd:Q3893120 ?pred ?item.
                            
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                              filter (?pred = wdt:P31 || ?pred = wdt:P279 || ?pred = wdt:P18 || ?pred = wdt:P373)
                            }
                            """)

    value = sparql_query(sparql)

    return render(
        request,
        'pao_de_mistura_info.html',
        {
            'value': value,
            'name': "Pão de Mistura"
        }
    )

# Retrieves the wikidata's inforation about Floar
def folar_info(request):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    query = sparql.setQuery("""
                            SELECT ?item ?itemLabel WHERE {
                              wd:Q1435311 ?pred ?item.
                            
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pt". }
                              filter (?pred = wdt:P31 || ?pred = wdt:P279 || ?pred = wdt:P18 || ?pred = wdt:P495)
                            }
                        """)

    value = sparql_query(sparql)

    return render(
        request,
        'folar_info.html',
        {
            'value': value,
            'name': "Folar"
        }
    )

# Process the query to obtain the information from the wikidata
def sparql_query(sparql):
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results_df = pd.io.json.json_normalize(results['results']['bindings'])
    results_df[['item.value', 'itemLabel.value']].head()
    value = results_df['itemLabel.value']

    return value

# Gets weather data
def get_weather():
    with open("bills/templates/weather.xml", "w") as f:
        f.write(requests.get("http://open.live.bbc.co.uk/weather/feeds/en/2742611/3dayforecast.rss").text)

    xslt_doc = etree.parse("bills/templates/weather.xsl")
    transform = etree.XSLT(xslt_doc)
    doc = etree.parse("bills/templates/weather.xml")
    result_tree = transform(doc)

    return result_tree

# Process the query to obtain the information from GraphDB
def query(str):
    query = str

    payload_query = {"query": query}
    try:
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        return res
    except Exception:
        payload_query = {"update": query}
        res = accessor.sparql_update(body=payload_query, repo_name=repo_name)
        print(res)

# Redirects to the home page
def redirect_to_home(request):
    return redirect(reverse_lazy('index'))


# XSLT transformation of original XML file
cwd = os.getcwd()
path = cwd + "/bills/templates"
dom = etree.parse(path + "/bakery_sales.xml")
xslt = etree.parse("xml_to_n3.xsl")
transform = etree.XSLT(xslt)

# RDF generation
rdf = transform(dom)
str_rdf = str(rdf)

# remove xml header (introduced by the lxml parser)
str_rdf = str_rdf.replace("<?xml version=\"1.0\"?>\n", "")

# save rdf as a .n3 file with enconding utf-8
with open(path + "//bakery_sales.n3", "w", encoding="utf-8") as file:
    file.write(str(str_rdf))

# upload the generated rdf file to repository (GraphDB error reading .n3 file!)
endpoint = "http://localhost:7200"
repo_name = "ProjEDC2"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)
#req = accessor.upload_data_file(path+"//bakery_sales.n3", repo_name=repo_name)
#print(req)

apply_inference()
apply_inference2()