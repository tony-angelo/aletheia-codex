/**
 * Firebase Functions for Aletheia Codex
 * Handles API endpoints for review, graph, and notes
 */

import {onRequest} from "firebase-functions/v2/https";
import {setGlobalOptions} from "firebase-functions/v2";
import * as logger from "firebase-functions/logger";

// Set global options for all functions
setGlobalOptions({maxInstances: 10});

// Review API Function
export const reviewapifunction = onRequest(
  {
    region: "us-central1",
    cors: true,
  },
  (request, response) => {
    logger.info("Review API called", {structuredData: true});

    // CORS headers
    response.header(
      "Access-Control-Allow-Origin",
      "https://aletheiacodex.app"
    );
    response.header(
      "Access-Control-Allow-Methods",
      "GET, POST, PUT, DELETE, OPTIONS"
    );
    response.header(
      "Access-Control-Allow-Headers",
      "Content-Type, Authorization"
    );

    if (request.method === "OPTIONS") {
      response.status(200).send("OK");
      return;
    }

    response.status(200).json({
      success: true,
      message: "Review API is working",
      timestamp: new Date().toISOString(),
      method: request.method,
      path: request.path,
      headers: request.headers,
    });
  }
);

// Notes API Function
export const notesapifunction = onRequest(
  {
    region: "us-central1",
    cors: true,
  },
  (request, response) => {
    logger.info("Notes API called", {structuredData: true});

    // CORS headers
    response.header(
      "Access-Control-Allow-Origin",
      "https://aletheiacodex.app"
    );
    response.header(
      "Access-Control-Allow-Methods",
      "GET, POST, PUT, DELETE, OPTIONS"
    );
    response.header(
      "Access-Control-Allow-Headers",
      "Content-Type, Authorization"
    );

    if (request.method === "OPTIONS") {
      response.status(200).send("OK");
      return;
    }

    response.status(200).json({
      success: true,
      message: "Notes API is working",
      timestamp: new Date().toISOString(),
      method: request.method,
      path: request.path,
      headers: request.headers,
    });
  }
);

// Graph API Function
export const graphfunction = onRequest(
  {
    region: "us-central1",
    cors: true,
  },
  (request, response) => {
    logger.info("Graph API called", {structuredData: true});

    // CORS headers
    response.header(
      "Access-Control-Allow-Origin",
      "https://aletheiacodex.app"
    );
    response.header(
      "Access-Control-Allow-Methods",
      "GET, POST, PUT, DELETE, OPTIONS"
    );
    response.header(
      "Access-Control-Allow-Headers",
      "Content-Type, Authorization"
    );

    if (request.method === "OPTIONS") {
      response.status(200).send("OK");
      return;
    }

    response.status(200).json({
      success: true,
      message: "Graph API is working",
      timestamp: new Date().toISOString(),
      method: request.method,
      path: request.path,
      headers: request.headers,
    });
  }
);
