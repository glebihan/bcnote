function _(string){
    return string;
}

var Application = function()
{
    EventsObject.call(this);
    this._init();
}

Application.prototype = Object.create(EventsObject.prototype);

Application.prototype._init = function()
{
    this.connector = new Connector(this);
    this._notebookList = new NotebookList(this);
    this._tagList = new TagList(this);
    this._noteEditor = new NoteEditor(this);
    this._noteList = new NoteList(this);
    this._noteEditor.on('ready', function()
    {
        this._noteEditor.update_height();
        this._noteList.update_height();
    }.bind(this));
    this._init_ui();
    
    this._tagList.on("tag_selected", this._update_search.bind(this));
    this._notebookList.on("notebook_selected", this._update_search.bind(this));
}

Application.prototype._update_search = function()
{
    this.connector.update_search({
        tag: this._tagList.get_selected(),
        notebook: this._notebookList.get_selected()
    });
}

Application.prototype._init_ui = function()
{
    jQuery("#leftbar").resizable({
        handles: "e",
        resize: function(event, ui){
            jQuery("#noteslist_wrapper").css("left", jQuery("#leftbar").outerWidth());
            jQuery("#noteeditor_wrapper").css("left", jQuery("#leftbar").outerWidth() + jQuery("#noteslist_wrapper").outerWidth());
        }
    });
    jQuery("#noteslist_wrapper").resizable({
        handles: "e",
        resize: function(event, ui){
            jQuery("#noteeditor_wrapper").css("left", jQuery("#leftbar").outerWidth() + jQuery("#noteslist_wrapper").outerWidth());
            jQuery("#searchbox").css("width", (jQuery("#noteslist_wrapper").width() - 32) + "px");
            jQuery("#search_filters").css("width", (jQuery("#noteslist_wrapper").width() - 10) + "px");
            jQuery("#noteslist_order_wrapper").css("width", (jQuery("#noteslist_wrapper").width() - 10) + "px");
            resize_search_input();
        }
    });
}

Application.prototype.run = function()
{
    jQuery(document).ready(function()
    {
        this._notebookList.reload();
        this._tagList.reload();
    }.bind(this));
}

var app;
jQuery(document).ready(function()
{
    app = new Application();
    app.run();
});
