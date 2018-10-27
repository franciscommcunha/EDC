<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <div style="background-color: darkorange; margin: 10px; margin-top: 0px; margin-bottom: 0px">
            <table style="margin: 0px; margin-bottom: 10px">
            <td style="vertical-align: middle">
                <xsl:element name="img">
                    <xsl:attribute name="src">
                        <xsl:value-of select="rss/channel/image/url"/>
                    </xsl:attribute>
                    <xsl:attribute name="align">
                        left
                    </xsl:attribute>
                    <xsl:attribute name="vertical-align">
                        middle
                    </xsl:attribute>
                </xsl:element>
            </td>
            <td>
                <xsl:element name="strong">
                    <xsl:value-of select="rss/channel/item/title"/>
                </xsl:element>
                <br/>
                <xsl:element name="a">
                    <xsl:attribute name="href">
                        <xsl:value-of select="rss/channel/item/link"/>
                    </xsl:attribute>
                    <xsl:attribute name="style">
                        color: white
                    </xsl:attribute>
                    <xsl:value-of select="rss/channel/item/description"/>
                </xsl:element>
                <br/>
            </td>
            </table>
        </div>
        <div style="background-color: orange; margin: 10px; margin-top: 0px; visibility: visible; display: block; padding-left: 0.3cm">
            <strong style="font-size: 0.9em">
                <xsl:value-of select="(rss/channel/item/title)[2]"/>
            </strong>
            <br/>
            <xsl:element name="a">
                <xsl:attribute name="href">
                    <xsl:value-of select="(rss/channel/item/link)[2]"/>
                </xsl:attribute>
                <xsl:attribute name="style">
                    color: white
                </xsl:attribute>
                <xsl:value-of select="(rss/channel/item/description)[2]"/>
            </xsl:element>
        </div>
        <div style="background-color: lightsalmon; margin: 10px; visibility: visible; display: block; padding-left: 0.3cm">
            <strong style="font-size: 0.9em">
                <xsl:value-of select="(rss/channel/item/title)[3]"/>
            </strong>
            <br/>
            <xsl:element name="a">
                <xsl:attribute name="href">
                    <xsl:value-of select="(rss/channel/item/link)[3]"/>
                </xsl:attribute>
                <xsl:attribute name="style">
                    color: white
                </xsl:attribute>
                <xsl:value-of select="(rss/channel/item/description)[3]"/>
            </xsl:element>
        </div>
        <div style="align-content: center; vertical-align: bottom; padding-left: 5cm; font-size: 0.3cm">
            <xsl:element name="a">
                <xsl:attribute name="href">
                    <xsl:value-of select="rss/channel/link"/>
                </xsl:attribute>
                <xsl:value-of select="rss/channel/title"/>,
            </xsl:element>
            <xsl:value-of select="rss/channel/description"/>,
            <xsl:value-of select="rss/channel/copyright"/>,
            Published: <xsl:value-of select="rss/channel/pubDate"/>
        </div>
    </xsl:template>
</xsl:stylesheet>