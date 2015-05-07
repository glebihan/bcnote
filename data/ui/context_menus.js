var ContextMenu = function(event){
    this._init(event);
}

ContextMenu.prototype = {
    _init: function(event){
        this._orig_event = event;
        
        var li, a;
        var menu_items = this._build_menu(event);
        this._html_element = jQuery("<ul class='context_menu'></ul>");
        li = jQuery("<li class='menu_title'></li>");
        li.appendTo(this._html_element);
        li.html(event.node.name);
        for (var i in menu_items){
            li = jQuery("<li></li>");
            a = jQuery("<a href='#'></a>");
            a.html(menu_items[i].label);
            a.appendTo(li);
            li.appendTo(this._html_element);
            
            a.click(this._on_link_clicked.bind(this, menu_items[i].action));
        }
        
        this._html_element.click(this._on_click.bind(this));
        jQuery(document).click(function(event){
            this._html_element.toggle(false);
        }.bind(this));
        
        this._html_element.css("top", (event.click_event.clientY - event.click_event.offsetY) + "px");
        this._html_element.css("left", event.click_event.clientX + "px");
    },
    
    _on_click: function(event){
        event.stopPropagation();
        event.preventDefault();
    },
    
    _on_link_clicked: function(action, event){
        event.stopPropagation();
        event.preventDefault();
    },
    
    show: function(){
        jQuery("ul.context_menu").toggle(false);
        this._html_element.appendTo("body");
        this._html_element.toggle(true);
        this._html_element[0].focus();
    }
}

var NotebooksListContextMenu = function(event){
    this._init(event);
}

NotebooksListContextMenu.prototype = {
    __proto__: ContextMenu.prototype,
    
    _build_menu: function(event){
        var res = new Array();
        res.push({action: "new_stack", label: _("New stack"), icon: "new"});
        res.push({action: "new_notebook", label: _("New notebook"), icon: "new"});
        return res;
    }
}
