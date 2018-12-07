Feature: The wishlist store service back-end
    As a Wishlist System Manager
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | id | name         | user     | entries   |
        |  1 | Mike's       | Mike     | Mac Pro   |
        |  2 | Sarah's      | Sarah    | iPhone    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I set the "name" to "Mike\'s"
    And I set the "user" to "Mike"
    And I set the "entries" to "Mac Pro"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see "1" in the result
    Then I should see "2" in the result

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "Mike\'s" in the "Name" field
    When I change "Name" to "My Wishlist"
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "My Wishlist" in the "Name" field
