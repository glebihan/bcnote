var EventsObject = function()
{
    this._callbacks = {};
    this._callback_id = 0;
}

EventsObject.prototype = {
    _trigger: function()
    {
        var eventName = arguments[0];
        if (this._callbacks[eventName])
        {
            for (var i in this._callbacks[eventName])
            {
                this._callbacks[eventName][i].apply(this, Array.prototype.slice.call(arguments, 1));
            }
        }
    },
    
    on: function(eventName, callback)
    {
        if (!this._callbacks[eventName])
        {
            this._callbacks[eventName] = {};
        }
        this._callback_id++;
        this._callbacks[eventName][this._callback_id] = callback;
        return this._callback_id;
    }
}
