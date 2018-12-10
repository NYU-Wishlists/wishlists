$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
		if (res.id!=null)
		{
			$("#wishlist_id").val(res.id);
		}
        $("#wishlist_user_name").val(res.user);
        $("#wishlist_name").val(res.name);
        $("#wishlist_entries").val(JSON.stringify(res.entries));
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_user_name").val("");
        $("#wishlist_name").val("");
        $("#wishlist_entries").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function update_table(res) {
      $("#search_results").empty();
      $("#search_results").append('<table class="table-striped">');
      var header = '<tr>'
      header += '<th style="width:10%">ID</th>'
      header += '<th style="width:10%">User</th>'
      header += '<th style="width:40%">Name</th>'
      header += '<th style="width:40%">Entries</th>'
      $("#search_results").append(header);
      for(var i = 0; i < res.length; i++) {
          wishlist = res[i];
          var row = "<tr><td>"+wishlist.id+"</td><td></td><td>"+wishlist.user+"</td><td>"+wishlist.name+"</td><td>"+JSON.stringify(wishlist.entries)+"</td></tr>";
          $("#search_results").append(row);
      }

      $("#search_results").append('</table>');
    }
    // ****************************************
    // Create a wishlist
    // ****************************************

    $("#create-btn").click(function () {

        var user = $("#wishlist_user_name").val();
        var name = $("#wishlist_name").val();
        var entries_str = $("#wishlist_entries").val();

        var entries = JSON.parse(entries_str.replace(/'/g, '"'));
        var data = {
            "name": name,
            "user": user,
            "entries": entries
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a wishlist
    // ****************************************

    $("#update-btn").click(function () {

      var user = $("#wishlist_user_name").val();
      var name = $("#wishlist_name").val();
      var entries_str = $("#wishlist_entries").val();
      var wishlist_id = $("#wishlist_id").val();

      if (wishlist_id==null)
      {
          flash_message("No ID in form")
          return
      }

      var entries = JSON.parse(entries_str.replace(/'/g, '"'));
      var data = {
          "name": name,
          "user": user,
          "entries": entries
      };

        var ajax = $.ajax({
                type: "PUT",
                url: "/wishlists/" + wishlist_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            //update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve Wishlits
    // ****************************************

    $("#retrieve-btn").click(function () {

      var wishlist_id = $("#wishlist_id").val();

      if (wishlist_id==null)
      {
          flash_message("No ID in form")
          return
      }
      var ajax = $.ajax({
          type: "GET",
          url: "/wishlists/" + wishlist_id
      })

      ajax.done(function(res){
         update_form_data(res)
          flash_message("wishlist with ID [" + wishlist_id + "] has been Retrived!")
      });

      ajax.fail(function(res){
          flash_message("Server error!")
      });
  });



    // ****************************************
    // Delete a wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        var wishlist_id = $("#wishlist_id").val();
        if (wishlist_id==null)
        {
            flash_message("No ID in form")
            return
        }
        var ajax = $.ajax({
            type: "DELETE",
            url: "/wishlists/" + wishlist_id
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("wishlist with ID [" + wishlist_id + "] has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Delete user's wishlists
    // ****************************************
    $("#delete-user-btn").click(function () {

        var user = $("#wishlist_user_name").val();
        if (user==null)
        {
            flash_message("No user name in form")
            return
        }
        var ajax = $.ajax({
            type: "DELETE",
            url: "/wishlists/" + user + "/delete_all"
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("wishlist of  user " + user + " has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a wishlist
    // ****************************************

    $("#search-btn").click(function () {

      var user = $("#wishlist_user_name").val();
      var name = $("#wishlist_name").val();

      var data = {
          "wishlist_name": name,
          "wishlist_user": user,
      };

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists?",
            data: data
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res[0])
            flash_message("Success")
            update_table(res)
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

      });
})
