var NoteList = function(app)
{
    EventsObject.call(this);
    this._app = app;
    this._init();
}

NoteList.prototype = Object.create(EventsObject.prototype);

NoteList.prototype._init = function()
{
    
}

NoteList.prototype.update_height = function()
{
    jQuery("#noteslist").css("height", (jQuery("#noteslist_wrapper").height() - jQuery("#noteslist_order_wrapper").outerHeight() - jQuery("#noteslist").offset().top) + "px");
}
