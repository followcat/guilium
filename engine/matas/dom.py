import engine.matas.base


class DomMata(engine.matas.base.BaseMata):

    jscodes = """
    var infoarr = [
    'padding', 'paddingTop', 'paddingBottom', 'paddingRight', 'paddingLeft',
    'margin', 'marginTop', 'marginBottom', 'marginRight', 'marginLeft',
    'content',
    "border", "borderBottom", "borderBottomColor", "borderBottomLeftRadius",
    "borderBottomRightRadius", "borderBottomStyle", "borderBottomWidth",
    "borderCollapse", "borderColor", "borderImage", "borderImageOutset",
    "borderImageRepeat", "borderImageSlice", "borderImageSource",
    "borderImageWidth", "borderLeft", "borderLeftColor", "borderLeftStyle",
    "borderLeftWidth", "borderRadius", "borderRight", "borderRightColor",
    "borderRightStyle", "borderRightWidth", "borderSpacing", "borderStyle",
    "borderTop", "borderTopColor", "borderTopLeftRadius", "borderTopRightRadius",
    "borderTopStyle", "borderTopWidth", "borderWidth"];

    function dump_dom ()
    {
        if (typeof(Node) == "undefined") {
            alert ("Sorry, this script doesn't work with Internet Explorer.");
            return;
        }
        dom_dict = traverse_nodes (document.body);
        return dom_dict;
    }

    function getTop(e) { 
        var offset=e.offsetTop; 
        if(e.offsetParent!=null) offset+=getTop(e.offsetParent); 
            return offset; 
    } 

    function getLeft(e) { 
        var offset=e.offsetLeft; 
        if(e.offsetParent!=null) offset+=getLeft(e.offsetParent); 
            return offset; 
    } 

    function css2json(css) {
        var s = {};
        if (css == null) {
            return s;
        }
        for (var i in infoarr) {
            var key = infoarr[i];
            if (key in css) {
                s[key] = [css[key]];
            }
        }
        return s;
    }

    function traverse_nodes (node)
    {
        var node_info = {
            'id': node.id,
            'name': node.nodeName,
            'class': node.className,
            'value': node.nodeValue,
            'nodetype': node.nodeType,
            'nodename': node.nodeName,
            'height': node.clientHeight,
            'width': node.clientWidth,
            'top': getTop(node),
            'left': getLeft(node),
            'attributes': [],
            'childNodes': [],
            'style': css2json(window.getComputedStyle(node, null)),
        };
        if (node.attributes && node.attributes.length) {
            for (var i = 0; i < node.attributes.length; ++i)
                node_info.attributes.push(traverse_nodes (node.attributes.item(i)));
        };
        if (node.childNodes && node.childNodes.length) {
            for (var i = 0; i < node.childNodes.length; ++i)
                node_info.childNodes.push(traverse_nodes (node.childNodes.item(i)));
        };
        return node_info;
    } 

    return dom_dict = dump_dom();
    """


class WebviewDomMata(DomMata):
    """"""
    def process(self, url, driver):
        driver.switch_to.context('CHROMIUM')
        driver.get(url)
        dom = driver.execute_script(self.jscodes)
        return dom


class DesktopDomMata(DomMata):
    """"""
    def process(self, url, driver):
        driver.get(url)
        dom = driver.execute_script(self.jscodes)
        return dom