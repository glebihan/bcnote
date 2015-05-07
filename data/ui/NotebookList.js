var NotebookList = function(app)
{
    EventsObject.call(this);
    this._app = app;
    this._init();
}

NotebookList.prototype = Object.create(EventsObject.prototype);

NotebookList.prototype._init = function()
{
    this._selectedNode = null;
    this._openNodes = new Array();
    jQuery("#notebookslist").tree({
        data: [],
        dragAndDrop: true,
        autoOpen: 0,
        onCanMove: function(node)
        {
            return (!node.is_stack);
        },
        onCanMoveTo: function(moved_node, target_node, position)
        {
            if (target_node.is_stack || target_node.id == -1)
            {
                return (position == 'inside');
            }
            else
            {
                return false;
            }
        }
    });
    jQuery("#notebookslist").bind('tree.select', function(event)
    {
        this._selectedNode = event.node;
        this._trigger("notebook_selected", this._selectedNode);
    }.bind(this));
    jQuery("#notebookslist").bind('tree.move', function(event)
    {
        if (event.move_info.target_node.id == -1)
        {
            alert("update_notebook_stack:" + event.move_info.moved_node.id + ":");
        }
        else
        {
            alert("update_notebook_stack:" + event.move_info.moved_node.id + ":" + event.move_info.target_node.id);
        }
    }.bind(this));
    jQuery("#notebookslist").bind('tree.open', function(event)
    {
        this._openNodes.push(event.node.id);
    }.bind(this));
    jQuery("#notebookslist").bind('tree.close', function(event)
    {
        var i = this._openNodes.indexOf(event.node.id);
        while (i != -1)
        {
            this._openNodes.splice(i, 1);
            i = this._openNodes.indexOf(event.node.id);
        }
    }.bind(this));
    jQuery("#notebookslist").bind('tree.contextmenu', function(event)
    {
        var menu = new NotebooksListContextMenu(event);
        menu.show();
    }.bind(this));
    
    this._app.connector.on("reload_notebooks", function(notebooks)
    {
        var notebooksTree = new Array();
        var currentStack = null;
        var currentStackName = null;
        var notebookNode;
        for (var i in notebooks)
        {
            notebookNode = {
                label: notebooks[i].name,
                id: notebooks[i].guid,
                is_stack: false
            };
            if (notebooks[i].stack != currentStackName)
            {
                if (currentStack != null)
                {
                    notebooksTree.push(currentStack);
                    currentStack = null;
                    currentStackName = null;
                }
                if (notebooks[i].stack)
                {
                    currentStack = {
                        label: notebooks[i].stack,
                        id: notebooks[i].stack,
                        children: new Array(),
                        is_stack: true
                    }
                    currentStackName = notebooks[i].stack;
                }
            }
            if (notebooks[i].stack)
            {
                currentStack.children.push(notebookNode);
            }
            else
            {
                notebooksTree.push(notebookNode);
            }
        }
        if (currentStack != null)
        {
            notebooksTree.push(currentStack);
        }
        jQuery("#notebookslist").tree("loadData", notebooksTree);
        
        for (var i in this._openNodes)
        {
            node = jQuery("#notebookslist").tree("getNodeById", this._openNodes[i]);
            if (node)
            {
                jQuery("#notebookslist").tree('openNode', node);
            }
        }
    }.bind(this));
}

NotebookList.prototype.reload = function()
{
    this._app.connector.reload_notebooks();
}

NotebookList.prototype.get_selected = function()
{
    return (this._selectedNode ? this._selectedNode.id : null);
}
