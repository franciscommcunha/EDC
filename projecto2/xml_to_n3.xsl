<?xml version="1.0"?>

	<!DOCTYPE rdf:RDF [
	      <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	      <!ENTITY ns "http://www.iro.umontreal.ca/lapalme/ns#">
		]
	>

<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:html="http://www.w3.org/1999/xhtml"
		xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
		xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
		xmlns:xs="http://www.w3.org/TR/2008/REC-xml-20081126#"
		xmlns:foaf="http://xmlns.com/foaf/spec/"
		>

	<xsl:strip-space elements="*"/>
	<xsl:output indent="yes" encoding="UTF-8"/>

	<!-- RDF Root -->
	<xsl:template match="/">
		<xsl:apply-templates/>	
	</xsl:template>

	<!-- Company -->
	<xsl:template match="CompanySales/Company">
		<!-- RDF Prefixes -->
		<xsl:text disable-output-escaping="yes">@prefix ns0: &lt;http://xmlns.com/foaf/spec/&gt; . &#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix product: &lt;http://www.padaria.com/products/&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix tax: &lt;http://www.padaria.com/products/tax/&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix company: &lt;http://www.padaria.com/company/&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix client: &lt;http://www.padaria.com/clients/&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix client_addr: &lt;http://www.padaria.com/clients/client_address&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix client_cont: &lt;http://www.padaria.com/clients/client_contact&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix client_trans: &lt;http://www.padaria.com/clients/transactions/&gt; .&#xa;</xsl:text>
		<xsl:text disable-output-escaping="yes">@prefix trans_time: &lt;http://www.padaria.com/clients/transactions/transaction_time&gt; .&#xa;</xsl:text>

		<!-- Company -->
		<xsl:text>company: &#xa;</xsl:text>
		<xsl:text>&#9;a ns0:Company</xsl:text>
		<xsl:text> ; &#xa;</xsl:text>

		<!-- CompanyId -->
		<xsl:text>&#9;ns0:comp_id </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="CompanyId"/>
		<xsl:text>"</xsl:text>
		<xsl:text> ; &#xa;</xsl:text>

		<!-- TaxRegistrationNumber -->
		<xsl:text>&#9;ns0:tax_number </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="TaxRegistrationNumber"/>
		<xsl:text>"</xsl:text>
		<xsl:text> ; &#xa;</xsl:text>

		<!-- CompanyName -->
		<xsl:text>&#9;ns0:name </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="CompanyName"/>
		<xsl:text>"</xsl:text>
		<xsl:text> ; &#xa;</xsl:text>

		<!-- BusinessName -->
		<xsl:text>&#9;ns0:busi_name </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="BusinessName"/>
		<xsl:text>"</xsl:text>
		<xsl:text> ; &#xa;</xsl:text>

		<!-- BusinessName -->
		<xsl:text>&#9;ns0:curr_code </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="CurrencyCode"/>
		<xsl:text>"</xsl:text>
		<xsl:text> ; &#xa;</xsl:text>

		<!-- Address -->
		<xsl:text>&#9;ns0:Address</xsl:text>
		<xsl:text> company:address ; &#xa;</xsl:text>

		<!-- Contact -->
		<xsl:text>&#9;ns0:Contact</xsl:text>
		<xsl:text> company:contact . &#xa;</xsl:text>

		<!-- company:address --> 
		<xsl:text>company:address&#xa;</xsl:text>
		<xsl:text>&#9;a ns0:Description ;&#xa;</xsl:text>
		<xsl:text>&#9;ns0:address </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="Address/AddressDetail"/>
		<xsl:text>"; &#xa;</xsl:text>
		<xsl:text>&#9;ns0:city </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="Address/City"/>
		<xsl:text>"; &#xa;</xsl:text>
		<xsl:text>&#9;ns0:postal </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="Address/PostalCode"/>
		<xsl:text>"; &#xa;</xsl:text>
		<xsl:text>&#9;ns0:country </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="Address/Country"/>
		<xsl:text>" . &#xa;</xsl:text>

		<!-- company:contact -->
		<xsl:text>company:contact&#xa;</xsl:text>
		<xsl:text>&#9;a ns0:Description ;&#xa;</xsl:text>
		<xsl:text>&#9;ns0:comp_telephone </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="Contact/Telephone"/>	
		<xsl:text>"; &#xa;</xsl:text>
		<xsl:text>&#9;ns0:comp_site </xsl:text>
		<xsl:text>"</xsl:text>
		<xsl:value-of select="Contact/Website"/>	
		<xsl:text>" . &#xa;</xsl:text>

	</xsl:template>

	<!-- CompanyProducts --> 
	<xsl:template match="CompanySales/CompanyProducts">

		<xsl:for-each select="Product">
			<xsl:text>product:</xsl:text>
			<xsl:value-of select="ProductID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:Product</xsl:text>
			<xsl:text>;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:prod_name </xsl:text>
			<xsl:text>"</xsl:text>
			<xsl:value-of select="ProductName"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:cost </xsl:text>
			<xsl:text>"</xsl:text>
			<xsl:value-of select="UnitCost"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:Tax tax:</xsl:text>
			<xsl:value-of select="ProductID"/>
			<xsl:text> .&#xa;</xsl:text>

			<xsl:text>tax:</xsl:text>
			<xsl:value-of select="ProductID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:Tax</xsl:text>
			<xsl:text> ;&#xa;</xsl:text>			
			<xsl:text>&#9;ns0:t_type "</xsl:text>
			<xsl:value-of select="Tax/TaxType"/>
			<xsl:text>" ;&#xa;</xsl:text>	

			<xsl:text>&#9;ns0:desc tax:</xsl:text>
			<xsl:if test="Tax/Description='Taxa Reduzida'">
				<xsl:text>reduced_tax .&#xa;</xsl:text>
			</xsl:if>
			<xsl:if test="Tax/Description='Taxa Intermedia'">
				<xsl:text>intermediate_tax .&#xa;</xsl:text>
			</xsl:if>
			<xsl:if test="Tax/Description='Taxa Normal'">
				<xsl:text>normal_tax .&#xa;</xsl:text>
			</xsl:if>

		</xsl:for-each>

		<!-- Taxa Reduzida -->
		<xsl:text>tax:reduced_tax&#xa;</xsl:text>
		<xsl:text>&#9;a ns0:</xsl:text>
		<xsl:text>Tax</xsl:text>
		<xsl:text> ;&#xa;</xsl:text>
		<xsl:text>&#9;ns0:tax_desc "Taxa Reduzida";&#xa;</xsl:text>
		<xsl:text>&#9;ns0:value "6" .&#xa;</xsl:text>

		<!-- Taxa Normal -->
		<xsl:text>tax:normal_tax&#xa;</xsl:text>
		<xsl:text>&#9;a ns0:</xsl:text>
		<xsl:text>Tax</xsl:text>
		<xsl:text> ;&#xa;</xsl:text>
		<xsl:text>&#9;ns0:tax_desc "Taxa Normal";&#xa;</xsl:text>
		<xsl:text>&#9;ns0:value "23" .&#xa;</xsl:text>

		<!-- Taxa Intermédia -->
		<xsl:text>tax:intermediate_tax&#xa;</xsl:text>
		<xsl:text>&#9;a ns0:</xsl:text>
		<xsl:text>Tax</xsl:text>
		<xsl:text> ;&#xa;</xsl:text>
		<xsl:text>&#9;ns0:tax_desc "Taxa Intermédia";&#xa;</xsl:text>
		<xsl:text>&#9;ns0:value "13" .&#xa;</xsl:text>
	
	</xsl:template>

	<xsl:template match="CompanySales/CompanyClients">
		<xsl:for-each select="Client">
			<!-- Client -->
			<xsl:text>client:</xsl:text>
			<xsl:value-of select="ClientID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:Clients</xsl:text>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_name </xsl:text>
			<xsl:text>"</xsl:text>
			<xsl:value-of select="ClientName"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:ClientAddress</xsl:text>
			<xsl:text> client_addr:</xsl:text>
			<xsl:value-of select="ClientID"/>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:ClientContact</xsl:text>
			<xsl:text> client_cont:</xsl:text>
			<xsl:value-of select="ClientID"/>
			<xsl:text> .&#xa;</xsl:text>

			<!-- ClientAddress -->
			<xsl:text>client_addr:</xsl:text>
			<xsl:value-of select="ClientID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:ClientAddress</xsl:text>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_address "</xsl:text>
			<xsl:value-of select="ClientAddress/AddressDetail"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_city "</xsl:text>
			<xsl:value-of select="ClientAddress/City"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_pc "</xsl:text>
			<xsl:value-of select="ClientAddress/PostalCode"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_region "</xsl:text>
			<xsl:value-of select="ClientAddress/Region"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_country "</xsl:text>
			<xsl:value-of select="ClientAddress/Country"/>
			<xsl:text>" .&#xa;</xsl:text>

			<!-- ClientContact --> 
			<xsl:text>client_cont:</xsl:text>
			<xsl:value-of select="ClientID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:ClientContact</xsl:text>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_tel "</xsl:text>
			<xsl:value-of select="ClientContact/Telephone"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_fax "</xsl:text>
			<xsl:value-of select="ClientContact/Fax"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:client_mail "</xsl:text>
			<xsl:value-of select="ClientContact/Email"/>
			<xsl:text>" .&#xa;</xsl:text>

		</xsl:for-each>

	</xsl:template>

	<xsl:template match="CompanySales/ClientsTransactions">

		<xsl:for-each select="Transaction">

			<!-- Transaction -->
			<xsl:text>client_trans:</xsl:text>
			<xsl:value-of select="TransactionID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:Transaction</xsl:text>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:trans_client client:</xsl:text>
			<xsl:value-of select="ClientID"/>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:trans_prod product:</xsl:text>
			<xsl:value-of select="ProductID"/>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:trans_prod_quant "</xsl:text>
			<xsl:value-of select="ProductQuantity"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:trans_total_cost "</xsl:text>
			<xsl:value-of select="TotalCost"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:TransactionTime</xsl:text>
		
			<xsl:text> trans_time:</xsl:text>
			<xsl:value-of select="TransactionID"/>			
			<xsl:text> .&#xa;</xsl:text>

			<!-- TransactionTime --> 
			<xsl:text>trans_time:</xsl:text>
			<xsl:value-of select="TransactionID"/>
			<xsl:text>&#xa;</xsl:text>
			<xsl:text>&#9;a ns0:TransactionTime</xsl:text>
			<xsl:text> ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:trans_date "</xsl:text>
			<xsl:value-of select="TransactionTime/Date"/>
			<xsl:text>" ;&#xa;</xsl:text>
			<xsl:text>&#9;ns0:trans_time "</xsl:text>
			<xsl:value-of select="TransactionTime/Time"/>
			<xsl:text>" .&#xa;</xsl:text>

		</xsl:for-each>

	</xsl:template>

</xsl:stylesheet>
