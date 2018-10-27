from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
import bills.BaseXClient
import datetime
import requests
from lxml import etree

"""
Sites visited for this project:
    https://www.tutorialspoint.com/python/python_xml_processing.html
"""


# Create your views here.
def index(request):
    xml = get_weather()

    return render(
        request,
        "index.html",
        {
            "xml": xml,
        })

def save_product_info(request):
    print(request.POST)

    p_id = request.POST.get("ProductID")
    price = request.POST.get("Price")
    name = request.POST.get("Name")
    tax_type = request.POST.get("TaxType")
    tax_desc = request.POST.get("TaxDescription")
    tax_value = request.POST.get("TaxValue")
    
    q_str = "xquery for $a in collection('bakery_sales')//CompanyProducts/Product " \
            "where contains ($a/ProductID, '{}') " \
            "return replace node $a with " \
            "<Product>" \
                "<ProductID>{}</ProductID>" \
                "<ProductName>{}</ProductName>" \
                "<UnitCost>{}</UnitCost>" \
                "<Tax>" \
                    "<TaxType>{}</TaxType>" \
                    "<Description>{}</Description>" \
                    "<TaxPercentage>{}</TaxPercentage>" \
                "</Tax>" \
            "</Product>".format(p_id,p_id,name,price,tax_type,tax_desc,tax_value)

    XMLinsert(q_str)
    
    p_info = [[]]
    p_info[0].append(price)
    p_info[0].append(tax_type)
    p_info[0].append(tax_desc)
    p_info[0].append(tax_value)

    return render(request,"info_products.html", 
        {
            "products" : p_info,
            "name" : name, 
        })

def edit_product_info(request):
    product_info = request.POST.get("product_info")
    product_name = request.POST.get("product_name")
    product_info = product_info.replace("[","").replace("]","").replace("\'","").split(",")

    p_info = {}
    p_info["name"] = product_name.lstrip()
    p_info["Price"] = product_info[0].lstrip()
    p_info["TaxType"] = product_info[1].lstrip()
    p_info["TaxDescription"] = product_info[2].lstrip()
    p_info["TaxValue"] = product_info[3].lstrip()
    p_info["ProductID"] = product_info[4].lstrip()

    return render(request,"edit_product_info.html", p_info)

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

    q_str = "xquery for $a in collection('bakery_sales')//CompanyClients/Client " \
            "where contains ($a/ClientID, '{}') " \
            "return replace node $a with " \
            "<Client>" \
                "<ClientID>{}</ClientID>" \
                "<ClientName>{}</ClientName>" \
                "<ClientAddress>" \
                    "<AddressDetail>{}</AddressDetail>" \
                    "<City>{}</City>" \
                    "<PostalCode>{}</PostalCode>" \
                    "<Region>{}</Region>" \
                    "<Country>{}</Country>" \
                "</ClientAddress>" \
                "<ClientContact>" \
                "<Telephone>{}</Telephone>" \
                "<Fax>{}</Fax>" \
                "<Email>{}</Email>" \
                "</ClientContact>" \
            "</Client>".format(c_id,c_id, name, address, city, postal, region, country, tel, fax, email)

    XMLinsert(q_str)

    # done this way to follow the criteria of clients_info and info_clients.html
    c_info = [[]]
    c_info[0].append(c_id)
    c_info[0].append(address)
    c_info[0].append(city)
    c_info[0].append(postal)
    c_info[0].append(region)
    c_info[0].append(country)
    c_info[0].append(tel)
    c_info[0].append(fax)
    c_info[0].append(email)

    return render(request, "info_clients.html",
            {
                "customers" : c_info,
                "name" : name
            })

def edit_client_info(request):

    client_info = request.POST.get("client_info")

    client_name = request.POST.get("client_name")

    client_info = client_info.replace("[","").replace("]","").replace("\'","").split(",")

    c_info = {}
    c_info["ID"] = client_info[0]
    c_info["Address"] = client_info[1].lstrip()
    c_info["City"] = client_info[2].lstrip()
    c_info["PostalCode"] = client_info[3].lstrip()
    c_info["Region"] = client_info[4].lstrip()
    c_info["Country"] = client_info[5].lstrip()
    c_info["Telephone"] = client_info[6].lstrip()
    c_info["Fax"] = client_info[7].lstrip()
    c_info["Email"] = client_info[8].lstrip()
    c_info["Name"] = client_name

    return render(request, "edit_client_info.html", c_info)

# Orders the search results based on selected input
def order_results(request):

    sort = request.POST.get("selected")
    search_val = request.POST.get("input")
    search_flag = request.POST.get("search_flag")
    count = request.POST.get("count")

    result = {}

    if sort == "a-z":
        q_str_prod = "for $a in collection('bakery_sales')//Product " \
                     "where contains($a/ProductName, '{}') " \
                     "order by $a//ProductName ascending " \
                     "return $a/ProductName/text()".format(search_val)

        q_str_client = "for $a in collection('bakery_sales')//Client " \
                       "where contains($a/ClientName, '{}') " \
                       "order by $a//ClientName ascending " \
                       "return $a/ClientName/text()".format(search_val)

        q_str_trans = "for $a in collection('bakery_sales')//Transaction " \
                      "where contains($a/ClientName, '{}') " \
                      "order by $a//TransactionID ascending " \
                      "return $a/ClientName/text()".format(search_val)

    elif sort == "z-a":
        q_str_prod = "for $a in collection('bakery_sales')//Product " \
                     "where contains($a/ProductName, '{}') " \
                     "order by $a//ProductName descending " \
                     "return $a/ProductName/text()".format(search_val)

        q_str_client = "for $a in collection('bakery_sales')//Client " \
                       "where contains($a/ClientName, '{}') " \
                       "order by $a//ClientName descending " \
                       "return $a/ClientName/text()".format(search_val)

        q_str_trans = "for $a in collection('bakery_sales')//Transaction " \
                      "where contains($a/ClientName, '{}') " \
                      "order by $a//TransactionID descending " \
                      "return $a/ClientName/text()".format(search_val)

    else:
        q_str_prod = "for $a in collection('bakery_sales')//Product " \
                     "where contains($a/ProductName, '{}') " \
                     "return $a/ProductName/text()".format(search_val)

        q_str_client = "for $a in collection('bakery_sales')//Client " \
                       "where contains($a/ClientName, '{}') " \
                       "return $a/ClientName/text()".format(search_val)

        q_str_trans = "for $a in collection('bakery_sales')//Transaction " \
                      "where contains($a/ClientName, '{}') " \
                      "return $a/ClientName/text()".format(search_val)

    result["value_sort"] = "clients"
    if sort == "products":  
        result["value_sort"] = "products"
    if sort == "transactions":  
        result["value_sort"] = "transactions"

    q_prod = XMLquery(q_str_prod)
    q_client = XMLquery(q_str_client)
    q_trans = XMLquery(q_str_trans)

    result["products"] = q_prod
    result["clients"] = q_client
    result["transactions"] = q_trans

    result["count"] = count
    result["search_flag"] = True
    result["input"] = search_val

    xml = get_weather()

    result["xml"] = xml
    
    return render(
        request,
        "index.html",
        result
    )


# Searches for the given string
def search(request):
    obj = request.GET.get('search')

    q_str_prod = "for $a in collection('bakery_sales')//Product " \
                 "where contains($a/ProductName, '{}') " \
                 "return $a/ProductName/text()".format(obj)

    q_str_client = "for $a in collection('bakery_sales')//Client " \
                   "where contains($a/ClientName, '{}') " \
                   "return $a/ClientName/text()".format(obj)

    q_str_trans = "for $a in collection('bakery_sales')//Transaction " \
                  "where contains($a/ClientName, '{}') " \
                  "return $a/ClientName/text()".format(obj)

    q_prod = XMLquery(q_str_prod)
    q_client = XMLquery(q_str_client)
    q_trans = XMLquery(q_str_trans)

    result = dict()
    result["products"] = q_prod
    result["clients"] = q_client
    result["transactions"] = q_trans

    cnt_p = [1 for p in result["products"]]
    cnt_c = [1 for p in result["clients"]]
    cnt_t = [1 for p in result["transactions"]]
    count = cnt_t + cnt_c + cnt_p
    count = sum(count)

    result["count"] = count
    result["search_flag"] = True
    result["input"] = obj
    result["value_sort"] = "clients" # default sorting value

    xml = get_weather()

    result["xml"] = xml

    return render(
        request,
        "index.html",
        result,
    )

# Add a client
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

        max_str = "for $a in collection('bakery_sales')//Client " \
                  "return $a/ClientID/text()"

        max_id = get_max(max_str)

        if name and address and postal and email:
            q_str = "xquery let $a := collection('bakery_sales')//CompanyClients " \
                    "return insert node " \
                    "<Client>" \
                    "<ClientID>{}</ClientID>" \
                    "<ClientName>{}</ClientName>" \
                    "<ClientAddress>" \
                        "<AddressDetail>{}</AddressDetail>" \
                        "<City>{}</City>" \
                        "<PostalCode>{}</PostalCode>" \
                        "<Region>{}</Region>" \
                        "<Country>{}</Country>" \
                    "</ClientAddress>" \
                    "<ClientContact>" \
                        "<Telephone>{}</Telephone>" \
                        "<Fax>{}</Fax>" \
                        "<Email>{}</Email>" \
                    "</ClientContact>" \
                    "</Client> into $a".format(max_id, name, address, city, postal, region, country, tel, fax, email)

            XMLinsert(q_str)

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

#add a product
def add_product(request):

    if "name" in request.POST and "cost" in request.POST and "type" in request.POST and "description" in request.POST and \
                    "percentage" in request.POST:
        name = request.POST["name"]
        cost = request.POST["cost"]
        type = request.POST["type"]
        description = request.POST["description"]
        percentage = request.POST["percentage"]

        max_str = "for $a in collection('bakery_sales')//Product " \
                  "return $a/ProductID/text()"

        max_id = get_max(max_str)

        if name and cost and type and percentage:
            q_str = "xquery let $a := collection('bakery_sales')//CompanyClients " \
                    "return insert node " \
                    "<Product>" \
                    "<ProductID>{}</ProductID>" \
                    "<ProductName>{}</ProductName>" \
                    "<UnitCost>{}</UnitCost>" \
                    "<Tax>" \
                        "<TaxType>{}</TaxType>" \
                        "<Description>{}</Description>" \
                        "<TaxPercentage>{}</TaxPercentage>" \
                    "</Tax>" \
                    "</Product> into $a".format(max_id, name, cost, type, description, percentage)

            XMLinsert(q_str)

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

# Lists all he products
def list_products(request):
    q_str = "for $a in collection('bakery_sales')//Product " \
            "return [$a/ProductID/text(),$a/ProductName/text()]"

    result = XMLquery(q_str)
    array = []

    for element in result:
        array += [element.replace("[", "").replace("]", "").split(',')]

    return render(
        request,
        "list_products.html",
        {
            "products": array,
        })


# Displays info about product
def info_products(request, name):
    # Warning! bug in split function in which it adds an additional space, so name is equal to " <name>"
    # to correct this bug use name[1:]!
    q_str = "declare function local:info($aname) " \
            "{ " \
            "for $b in collection('bakery_sales')//Product " \
            "where $b/ProductName = $aname " \
            "return [$b/UnitCost/text(),$b/Tax/TaxType/text(),$b/Tax/Description/text(),$b/Tax/TaxPercentage/text(),$b/ProductID/text()] " \
            "}; " \
            "let $c := local:info('"+name[1:]+"') " \
            "return $c"

    result = XMLquery(q_str)
    prod_array = []

    for element in result:
        aux = element.replace("[", "").replace("]", "").split(',')
        aux = [i if i != " ()" else "" for i in aux]
        prod_array += [aux]

    return render(
        request,
        "info_products.html",
        {
            "products": prod_array,
            "name": name,
        }
    )


# Lists all the clients
def list_clients(request):

    q_str = "for $a in collection('bakery_sales')//Client " \
            "order by $a/ClientID " \
            "return [$a/ClientID/text(),$a/ClientName/text(),$a/ClientAddress/AddressDetail/text()]"

    result = XMLquery(q_str)
    array = []

    for element in result:
        array += [element.replace("[", "").replace("]", "").split(',')]

    return render(
        request,
        "list_clients.html",
        {
            "customers": array,
        })


#  Given a client, shows its info
def clients_info(request, name):
    # Warning! bug in split function in which it adds an additional space, so name is equal to " <name>"
    # to correct this bug use name[1:]!
    q_str = "declare function local:info($aname) " \
            "{" \
            "for $b in collection('bakery_sales')//Client " \
            "where contains($b/ClientName, $aname) " \
            "return [$b/ClientID/text(),$b/ClientAddress/AddressDetail/text(),$b/ClientAddress/City/text(), " \
            "$b/ClientAddress/PostalCode/text(),$b/ClientAddress/Region/text(),$b/ClientAddress/Country/text(), " \
            "$b/ClientContact/Telephone/text(),$b/ClientContact/Fax/text(),$b/ClientContact/Email/text()] " \
            "}; " \
            "let $c := local:info('"+name[1:]+"')" \
            "return $c"

    result = XMLquery(q_str)

    cst_array = []

    for element in result:
        aux = element.replace("[", "").replace("]", "").split(',')
        aux = [i if i != " ()" else "" for i in aux]
        cst_array += [aux]

    return render(
        request,
        'info_clients.html',
        {
            'customers': cst_array,
            'name': name
        }
    )

# List all the taxes
def list_taxes(request):

    q_str = "for $a in collection('bakery_sales')//Product order by $a/Tax/TaxPercentage/text() descending " \
            "return [$a/Tax/TaxType/text(),$a/Tax/Description/text(),$a/Tax/TaxPercentage/text()]"

    result = XMLquery(q_str)

    tax_array = []

    for element in result:
        elem = element.replace("[", "").replace("]", "").split(',')

        if elem not in tax_array:
            tax_array += [elem]

    return render(
        request,
        'list_taxes.html',
        {
            'taxes': tax_array,
        }
    )

# Given a tax shows it's products
def info_tax(request, name):
    # Warning! bug in split function in which it adds an additional space, so name is equal to " <name>"
    # to correct this bug use name[1:]!
    q_str = "declare function local:info($aname) " \
            "{ " \
            "for $b in collection('bakery_sales')//Product " \
            "where contains($b/Tax/Description, $aname) " \
            "return [$b/ProductName/text()] " \
            "}; " \
            "let $c := local:info('"+name[1:]+"') " \
            "return $c"

    result = XMLquery(q_str)

    tax_array = []

    for element in result:
        aux = element.replace("[", "").replace("]", "").split(',')
        aux = [i if i != " ()" else "" for i in aux]
        tax_array += [aux]

    return render(
        request,
        'info_tax.html',
        {
            'taxes': tax_array,
            'name': name,
        }
    )

# Adds a sale
def add_sale(request):

    if "client_id" in request.POST and "prod_id" in request.POST and "quant" in request.POST:

        client_id = request.POST["client_id"]
        prod_id = request.POST["prod_id"]
        quant = request.POST["quant"]

        if client_id and prod_id and quant:

            # obter o id da ultima transaçao e incrementar para a nova transacao
            q_id = "for $a in collection('bakery_sales')//Transaction return [$a/TransactionID/text()]"

            res_id = XMLquery(q_id)

            trans_id = len(res_id) + 1

            # através do id do cliente obter o seu nome para adicionar automaticamente
            q_client = "declare function local:get_name($id) " \
                       "{ " \
                       "for $b in collection('bakery_sales')//Client where contains($b/ClientID,$id) " \
                       "return $b/ClientName/text() " \
                       "}; " \
                       "let $c := local:get_name('"+client_id[1:]+"') " \
                       "return $c"

            c_name = XMLquery(q_client)

            # através do productID obter o seu nome respectivamente para adicionar automaticamente
            q_prod = "declare function local:get_prod($id) " \
                     "{ " \
                     "for $b in collection('bakery_sales')//Product where contains($b/ProductID,$id) " \
                     "return $b/ProductName/text() " \
                     "}; " \
                     "let $c := local:get_prod('"+prod_id+"') " \
                     "return $c"

            p_name = XMLquery(q_prod)

            # através do productID obter o seu preco respetivamente para adicinar o custo total automaticamente
            q_price = "declare function local:get_price($id) " \
                      "{ " \
                      "for $b in collection('bakery_sales')//Product where contains($b/ProductID,$id) " \
                      "return $b/UnitCost/text() " \
                      "}; " \
                      "let $c := local:get_price('"+prod_id+"') " \
                      "return $c"

            p_price = XMLquery(q_price)
            money = int(quant) * float(p_price[0])

            q_str = "xquery let $a := collection('bakery_sales')//ClientsTransactions " \
                    "return insert node " \
                    "<Transaction>" \
                    "<TransactionID> {} </TransactionID>" \
                    "<ClientID> {} </ClientID>" \
                    "<ClientName>{}</ClientName>" \
                    "<ProductID> {} </ProductID>" \
                    "<ProductName> {} </ProductName>" \
                    "<ProductQuantity> {} </ProductQuantity>" \
                    "<TotalCost> {} </TotalCost>" \
                    "<TransactionTime>" \
                    "<Date> {} </Date>" \
                    "<Time> {} </Time>" \
                    "</TransactionTime>" \
                    "</Transaction> into $a".format(trans_id, client_id, c_name[0], prod_id, p_name[0], quant, money,
                                                    datetime.datetime.now().strftime("%H:%M"), datetime.datetime.now().strftime("%d/%m/%y"))
            XMLinsert(q_str)

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


# Shows all made sales
def list_sales(request):

    q_str = "for $a in collection('bakery_sales')//Transaction " \
            "return [$a/TransactionID/text(),$a/ClientID/text()]"

    result = XMLquery(q_str)
    id_sales_array = []

    for element in result:
        t_id = element.replace("[", "").replace("]", "").split(",")[0]
        c_id = element.replace("[", "").replace("]", "").split(",")[1]
        q2_str = "for $a in collection('bakery_sales')//Client " \
                 "where $a/ClientID = {} " \
                 "return $a/ClientName/text()".format(c_id)
        id_sales_array += [(t_id, str(XMLquery(q2_str)).replace("[", "").replace("]", "").replace("'", ""))]

    return render(
        request,
        'list_sales.html',
        {
            'sales': id_sales_array,
        }
    )

# Given a client shows the sales made for him
def info_sales(request, name):

    q_str = "for $a in collection('bakery_sales')//Transaction " \
            "where $a/ClientName = '"+name+"' " \
            "return [$a/ProductName/text(), $a/ProductQuantity/text(), $a/TotalCost/text(), $a/TransactionTime/Date/text(), $a/TransactionTime/Time/text()]"

    result = XMLquery(q_str)
    sales_array = []

    for element in result:
        aux = element.replace("[", "").replace("]", "").split(",")
        aux = [x if x != "()" else "" for x in aux]
        sales_array += [aux]

    return render(
        request,
        'info_sales.html',
        {
            'sales': sales_array,
            'name': name,
        }
    )


# Gets weather data
def get_weather():
    with open("bills/templates/weather.xml", "w") as f:
    	f.write(requests.get("http://open.live.bbc.co.uk/weather/feeds/en/2742611/3dayforecast.rss").text)

    xslt_doc = etree.parse("bills/templates/weather.xsl")
    transform = etree.XSLT(xslt_doc)
    doc = etree.parse("bills/templates/weather.xml")
    result_tree = transform(doc)

    return result_tree

# Process the query
def XMLquery(str):
    session = bills.BaseXClient.Session("localhost", 1984, "admin", "admin")
    lst = []

    try:
        query = session.query(str)
        for i, elem in query.iter():
            lst += [elem]
        query.close()
    finally:
        if session:
            session.close()

    return lst


# Returns the biggest number from an int array given by
# an xquery, for example, the biggest client's id
def get_max(str):
    res = XMLquery(str)
    lst = []
    for i in res:
        lst += [i]
    return int(max(lst)) + 1


# Insert data into the xml database
def XMLinsert(str):
    session = bills.BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    try:
        session.execute(str)
    finally:
        if session:
            session.close()

# Redirects to home
def redirect_to_home(request):
    return redirect(reverse_lazy('index'))
