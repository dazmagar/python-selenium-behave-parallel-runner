@smoke
Feature: Test2 feature


    @2222 @serial
    Scenario: Test2 - 1
        Given I open Github URL in browser
        And I see "GitHub" in title
        When I search "user:dimbbass" text
        And I see repositories associated with user and its count greater than "1"
        When I navigate into repo with name "docker-react"
        And I see that repo "docker-react" belongs to "Dimbbass" author

    @2222 @serial
    Scenario: Test2 - 2
        Given I open Github URL in browser
        And I see "GitHub" in title
        When I search "user:dazmagar" text
        And I see repositories associated with user and its count greater than "1"
        When I navigate into repo with name "test-apache"
        And I see that repo "test-apache" belongs to "dazmagar" author

    @2222 @serial
    Scenario: Test2 - 3
        Given I open Github URL in browser
        And I see "GitHub" in title
        When I search "user:derr22" text
        And I see repositories associated with user and its count greater than "1"
        When I navigate into repo with name "Crypto11"
        And I see that repo "Crypto11" belongs to "Derr22" author
