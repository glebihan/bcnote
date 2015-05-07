var Connector = function(app)
{
    EventsObject.call(this);
    this._app = app;
    this._init();
}

Connector.prototype = Object.create(EventsObject.prototype);

Connector.prototype._init = function()
{
}

Connector.prototype.reload_notebooks = function()
{
    this._send_command("reload_notebooks");
}

Connector.prototype.reload_tags = function()
{
    this._send_command("reload_tags");
}

Connector.prototype.update_search = function(params)
{
    this._send_command("update_search", params);
}

Connector.prototype._send_command = function()
{
    var command = null, params = new Array();
    for (var i in arguments)
    {
        if (i == 0) command = arguments[i];
        else params.push(arguments[i]);
    }
    alert("!cmd:" + command + ":" + JSON.stringify(params));
}
