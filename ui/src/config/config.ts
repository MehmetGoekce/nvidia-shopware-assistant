// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Configuration file for the Shopping Assistant UI
 */

export interface AppConfig {
  api: {
    baseUrl: string;
    port: number;
    endpoints: {
      query: string;
      stream: string;
      health: string;
    };
  };
  ui: {
    defaultImages: {
      fashion: string;
    };
    categories: {
      beauty: string;
      fashion: string;
      grocery: string;
      office: string;
      lifestyle: string;
      lastCall: string;
    };
    categoryPrompts: {
      beauty: string;
      fashion: string;
      grocery: string;
      office: string;
      lifestyle: string;
      lastCall: string;
    };
  };
  features: {
    guardrails: {
      enabled: boolean;
      defaultState: boolean;
    };
    imageUpload: {
      enabled: boolean;
      maxSize: number; // in MB
      allowedTypes: string[];
    };
  };
}

// Get configuration based on environment
const getConfig = (): AppConfig => {
  // Always use nginx proxy - it handles the routing
  const baseUrl = '/api';

  return {
    api: {
      baseUrl: baseUrl,
      port: 80,
      endpoints: {
        query: '/query',
        stream: '/query/stream',
        health: '/health',
      },
    },
    ui: {
      defaultImages: {
        fashion: "/images/splash.jpg",
      },
      categories: {
        beauty: "BEAUTY & WELLNESS",
        fashion: "MODE",
        grocery: "ACCESSOIRES",
        office: "SCHUHE",
        lifestyle: "TASCHEN",
        lastCall: "SALE"
      },
      categoryPrompts: {
        beauty: "Zeig mir Beauty & Wellness Produkte",
        fashion: "Zeig mir Mode",
        grocery: "Zeig mir Accessoires",
        office: "Zeig mir Schuhe",
        lifestyle: "Zeig mir Taschen",
        lastCall: "Zeig mir Sale Angebote",
      }
    },
    features: {
      guardrails: {
        enabled: true,
        defaultState: true,
      },
      imageUpload: {
        enabled: true,
        maxSize: 10, // 10MB
        allowedTypes: ['image/jpeg', 'image/png'],
      },
    },
  };
};

export const config = getConfig();

// Helper functions
export const getApiUrl = (endpoint: keyof AppConfig['api']['endpoints']): string => {
  return `${config.api.baseUrl}${config.api.endpoints[endpoint]}`;
};

export const isFashionMode = (): boolean => {
  return true; // Always return true - always fashion mode
};

export const getDefaultImage = (): string => {
  return config.ui.defaultImages.fashion; // Always use fashion image
}; 