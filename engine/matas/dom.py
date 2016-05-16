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

    function unDisplay(e) {
        var pos = window.getComputedStyle(e, null).position;
        if(pos=='fixed') {
            return true;
        }
        else return false;
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

    function getElementOffset(e) {
        var t = e.offsetTop;
        var l = e.offsetLeft;
        var w = e.offsetWidth;
        var h = e.offsetHeight;
        var mh = parseInt(window.getComputedStyle(e, null).marginTop) + parseInt(window.getComputedStyle(e, null).marginBottom);

        while(e=e.offsetParent) {
            t+=e.offsetTop;
            l+=e.offsetLeft;
        }
        return {
            top : t,
            left : l,
            width : w,
            height : h,
            marginheight : mh
        }
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

    function parentNodeName (node)
    {
        if (node.parentNode!=null) {
            var parentName = parentNodeName (node.parentNode);
            parentName += '-' + node.parentNode.className;
            return parentName
        }
        else return '';
    }

    function traverse_nodes (node)
    {
        var offset = getElementOffset(node)
        var node_info = {
            'id': node.id,
            'name': node.nodeName,
            'innerText': node.innerText,
            'class': node.className,
            'value': node.nodeValue,
            'nodetype': node.nodeType,
            'nodename': node.nodeName,
            'height': offset['height'],
            'width': offset['width'],
            'top': offset['top'],
            'left': offset['left'],
            'marginheight': offset['marginheight'],
            'attributes': [],
            'childNodes': [],
            'parentNode': parentNodeName (node)
        };
        try {
            node_info['style'] = css2json(window.getComputedStyle(node, null));
        } catch(error) {
            node_info['style'] = {};
        }
        if (node.childNodes && node.childNodes.length) {
            for (var i = 0; i < node.childNodes.length; ++i) {
                if (node.childNodes.item(i).nodeType == 2 | node.childNodes.item(i).nodeType == 3 | node.childNodes.item(i).nodeType == 8) {
                    continue;
                };
                if (unDisplay(node.childNodes.item(i))) {
                    continue;
                }
                node_info.childNodes.push(traverse_nodes (node.childNodes.item(i)));
            };
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
        self.scrollfullscreen(driver)
        dom = driver.execute_script(self.jscodes)
        return dom


class DesktopDomMata(DomMata):
    """"""
    def process(self, url, driver):
        driver.get(url)
        self.scrollfullscreen(driver)
        dom = driver.execute_script(self.jscodes)
        return dom
