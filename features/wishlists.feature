Feature: The wishlist store service back-end
    As a Wishlist System Manager
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | name         | user     | entries   |
        | Mikes       | Mike     | Mackbook, Iphone   |
        | Sarah's      | Sarah    |  Toy	|

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists demo REST API Service" in the title
    And I should not see "404 Not Found"



Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Mike" in the results
    

Scenario: Read a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Mikes" in the "Name" field
    When I change "Name" to "Mikes"
	And I change "user_name" to "Mike"
	When I press the "Retrieve" button
    Then I should see "Mikes" in the "Name" field
	
Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Mikes" in the "Name" field
    When I change "Name" to "My Wishlist"
    And I press the "Update" button
    Then I should see the message "Success"
	When I press the "Retrieve" button
    Then I should see "My Wishlist" in the "Name" field

Scenario: Delete a Wishlist
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Mikes" in the "Name" field
    When I press the "Delete" button
    Then I should see the message "Deleted!"
	When I press the "Search" button
    Then I should not see "Mikes" in the results
	
	
Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "name" to "Franks"
    And I set the "user_name" to "Frank"
    And I set the "entries" to "[{'id':0, 'name':'toy'}, {'id':1, 'name':'gift'}]"
    And I press the "Create" button
    Then I should see the message "Success"