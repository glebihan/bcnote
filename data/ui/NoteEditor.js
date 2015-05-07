var NoteEditor = function(app)
{
    EventsObject.call(this);
    this._app = app;
    this._init();
}

NoteEditor.prototype = Object.create(EventsObject.prototype);

NoteEditor.prototype._init = function()
{
    tinymce.init({
        selector: "#tinymcecontainer",
        setup: function(editor){
            editor.on('change', function(e){
                alert('set_note_contents:' + editing_note_local_id + ':' + editor.getContent());
            }.bind(this));
            editor.on('init', function(e){
                setTimeout(function(){
                    this._trigger('ready');
                }.bind(this), 100);
            }.bind(this));
        }.bind(this),
        menubar: false,
        statusbar: false,
        toolbar: "bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | formatselect fontselect fontsizeselect | cut copy paste | bullist numlist | outdent indent | blockquote | undo redo | removeformat subscript superscript"
    });
    
    jQuery("#note_title").change(function(event){
        alert("set_note_title:" + editing_note_local_id + ":" + jQuery("#note_title").val());
    });
 
    jQuery("#note_tags_selector")
        // don't navigate away from the field on tab when selecting an item
        .bind("keydown", function(event){
            if (event.keyCode === jQuery.ui.keyCode.TAB && jQuery(this).data("ui-autocomplete").menu.active){
                event.preventDefault();
            }
        })
        .bind("keypress", function(event){
            if (event.keyCode === jQuery.ui.keyCode.ENTER){
                var tag = jQuery(this).val();
                if (tag){
                    var selected_tags = new Array();
                    jQuery("#note_tags_list").find("span.tag").each(function(index){
                        selected_tags.push(jQuery(this).text());
                    });
                    if (selected_tags.indexOf(tag) == -1){
                        push_note_tag(tag);
                        jQuery(this).val("");
                        alert("add_note_tag:" + editing_note_local_id + ":" + tag);
                        jQuery(this).autocomplete("close");
                        update_notes_filter();
                    }
                }
            }
        })
        .autocomplete({
            minLength: 1,
            source: function(request, response){
                var selected_tags = new Array();
                jQuery("#note_tags_list").find("span.tag").each(function(index){
                    selected_tags.push(jQuery(this).text());
                });
                var matches = jQuery.ui.autocomplete.filter(availableTags, request.term);
                var res = new Array();
                for (var i in matches){
                    if (selected_tags.indexOf(matches[i]) == -1){
                        res.push(matches[i]);
                    }
                }
                response(res);
            },
            focus: function(){
                // prevent value inserted on focus
                return false;
            },
            select: function(event, ui){
                push_note_tag(ui.item.value);
                jQuery(this).val("");
                alert("add_note_tag:" + editing_note_local_id + ":" + ui.item.value);
                update_notes_filter();
                return false;
            }
        });
}

NoteEditor.prototype.update_height = function()
{
    jQuery("#tinymcecontainer_ifr").css("height", (jQuery("#noteeditor_inside_wrapper").height() - jQuery("#tinymcecontainer_ifr").offset().top) + "px");
}
