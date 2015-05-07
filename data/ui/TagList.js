var TagList = function(app)
{
    EventsObject.call(this);
    this._app = app;
    this._init();
}

TagList.prototype = Object.create(EventsObject.prototype);

TagList.prototype._init = function()
{
    this._selectedNode = null;
    this._openNodes = new Array();
    jQuery("#tagslist").tree({
        data: []
    });
    jQuery("#tagslist").bind('tree.select', function(event)
    {
        this._selectedNode = event.node;
        this._trigger("tag_selected", this._selectedNode);
    }.bind(this));
    jQuery("#tagslist").bind('tree.open', function(event)
    {
        this._openNodes.push(event.node.id);
    }.bind(this));
    jQuery("#tagslist").bind('tree.close', function(event)
    {
        var i = this._openNodes.indexOf(event.node.id);
        while (i != -1)
        {
            this._openNodes.splice(i, 1);
            i = this._openNodes.indexOf(event.node.id);
        }
    }.bind(this));
    
    this._app.connector.on("reload_tags", function(tags)
    {
        var tagsTree = new Array();
        var currentParent = null;
        var currentParentName = null;
        var tagNode;
        for (var i in tags)
        {
            tagNode = {
                label: tags[i].name,
                id: tags[i].guid
            };
            if (tags[i].parent != currentParentName)
            {
                if (currentParent != null)
                {
                    tagsTree.push(currentParent);
                    currentParent = null;
                    currentParentName = null;
                }
                if (tags[i].parent)
                {
                    currentParent = {
                        label: tags[i].parent,
                        id: tags[i].parentGuid,
                        children: new Array()
                    }
                    currentParentName = tags[i].parent;
                }
            }
            if (tags[i].parent)
            {
                currentParent.children.push(tagNode);
            }
            else
            {
                tagsTree.push(tagNode);
            }
        }
        if (currentParent != null)
        {
            tagsTree.push(currentParent);
        }
        jQuery("#tagslist").tree("loadData", tagsTree);
        
        for (var i in this._openNodes)
        {
            node = jQuery("#tagslist").tree("getNodeById", this._openNodes[i]);
            if (node)
            {
                jQuery("#tagslist").tree('openNode', node);
            }
        }
    }.bind(this));
}

TagList.prototype.reload = function()
{
    this._app.connector.reload_tags();
}

TagList.prototype.get_selected = function()
{
    return (this._selectedNode ? this._selectedNode.id : null);
}
