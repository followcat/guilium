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
        try {
            var pos = window.getComputedStyle(e, null).position;
        } catch(error) {
            var pos = 'notfixed';
        }
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
        try {
            var mt = parseInt(window.getComputedStyle(e, null).marginTop);
            var mb = parseInt(window.getComputedStyle(e, null).marginBottom);
        } catch(error) {
            var mt = 0;
            var mb = 0;
        }

        while(e=e.offsetParent) {
            t+=e.offsetTop;
            l+=e.offsetLeft;
        }
        return {
            top : t,
            left : l,
            width : w,
            height : h,
            margintop : mt,
            marginbottom : mb
        }
    }

    function toRGB(str){
        var reg = /#[0-9a-fA-F]{3,6}/;
        if (!reg.test(str)) {
            return str
        }
        match_list = str.match(reg)
        for (var i in match_list) {
            sub_str = match_list[i];
            var replace_str = sub_str;
            if(sub_str.length == 4 || sub_str.length == 7){
                if(sub_str.length == 4){
                    replace_str = replace_str + replace_str.slice(1);
                }
                var n = replace_str.slice(1);
                var arr = new Array();
                arr[0] = parseInt(n.slice(0,2),16);
                arr[1] = parseInt(n.slice(2,4),16);
                arr[2] = parseInt(n.slice(4,6),16); 
                replace_str = 'rgb(' + arr.join(', ') + ")";
                str = str.replace(sub_str, replace_str);
            }
        }
        return str
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
            parentName += '<SEP>' + node.className;
            return parentName
        }
        else return '';
    }

    function styleInfo (node)
    {
        var style_info = {};
        try {
            if (node.currentStyle) {
                current_style = node.currentStyle;
                for (var i in current_style) {
                    var key = current_style[i];
                    style_info[i] = toRGB(key);
                }
            }
            else {
                style_info = window.getComputedStyle(node, null);
            }
        } catch(error) {}
        return style_info;
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
            'marginTop': offset['margintop'],
            'marginBottom': offset['marginbottom'],
            'attributes': [],
            'childNodes': [],
            'parentNode': parentNodeName (node)
        };

        node_info['style'] = css2json(styleInfo(node));

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
        return driver.execute_script(self.jscodes)


class DesktopDomMata(DomMata):
    """"""
    def process(self, url, driver):
        return driver.execute_script(self.jscodes)
