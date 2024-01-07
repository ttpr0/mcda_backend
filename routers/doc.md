# API-Routers

This package contains all API-handlers of the mcda-backend.

## app_state.py

State router to handle requests concerning available parameters.

Expected behavior:
    -> request app_state-API for available parameters
    -> select parameters from avaiable
    -> send request with selected parameters to one of the other APIs

Requests are expected to happen on Front-End initialization to populate the *vuex* tool-states.

For Layout of responses see provided doc-strings.
Reponses usually contain *i18n*-keys to be handled by the frontend localization instead of actuall names/text.

## decision_support.py

Multi-Criteria Decision-Support API-handler.

## spatial_access.py

Two-Step-Floating-Catchment-Area API-handler.
