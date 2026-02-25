// DataHaven MSP Service - Storage Provider & Authentication
import { MspClient } from '@storagehub-sdk/msp-client';
import { getConnectedAddress, getWalletClient } from './clientService';
import { NETWORKS } from '../config/networks';

// Storage keys
const SESSION_TOKEN_KEY = 'datahaven_session_token';
const USER_PROFILE_KEY = 'datahaven_user_profile';

// State
let mspClientInstance = null;
let sessionToken = undefined;
let authenticatedUserProfile = null;

// Initialize state from storage
function initFromStorage() {
  if (typeof window === 'undefined') return;

  const storedToken = sessionStorage.getItem(SESSION_TOKEN_KEY);
  const storedProfile = sessionStorage.getItem(USER_PROFILE_KEY);

  if (storedToken) {
    sessionToken = storedToken;
  }
  if (storedProfile) {
    try {
      authenticatedUserProfile = JSON.parse(storedProfile);
    } catch {
      // Invalid stored profile, ignore
    }
  }
}

// Initialize on module load
initFromStorage();

// Session provider for authenticated requests
const sessionProvider = async () => {
  const address = getConnectedAddress();
  return sessionToken && address ? { token: sessionToken, user: { address } } : undefined;
};

// Connect to MSP
export async function connectToMsp() {
  if (mspClientInstance) {
    return mspClientInstance;
  }

  const httpCfg = { baseUrl: NETWORKS.testnet.mspUrl };
  mspClientInstance = await MspClient.connect(httpCfg, sessionProvider);
  return mspClientInstance;
}

// Get MSP client instance
export function getMspClient() {
  if (!mspClientInstance) {
    throw new Error('MSP client not connected. Please connect to MSP first.');
  }
  return mspClientInstance;
}

// Check if MSP is connected
export function isMspConnected() {
  return mspClientInstance !== null;
}

// Get MSP health status
export async function getMspHealth() {
  const client = getMspClient();
  const health = await client.info.getHealth();
  return health;
}

// Get MSP information
export async function getMspInfo() {
  const client = getMspClient();
  const info = await client.info.getInfo();
  return info;
}

// Authenticate user via SIWE (Sign-In With Ethereum)
export async function authenticateUser() {
  const client = getMspClient();
  const walletClient = getWalletClient();

  const domain = window.location.hostname || 'localhost';
  const uri = window.location.origin || 'http://localhost';

  const siweSession = await client.auth.SIWE(walletClient, domain, uri);
  sessionToken = siweSession.token;

  const profile = await client.auth.getProfile();
  authenticatedUserProfile = profile;

  // Persist to session storage
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(SESSION_TOKEN_KEY, sessionToken);
    sessionStorage.setItem(USER_PROFILE_KEY, JSON.stringify(profile));
  }

  return profile;
}

// Get value propositions
export async function getValueProps() {
  const client = getMspClient();
  const valueProps = await client.info.getValuePropositions();

  if (!Array.isArray(valueProps) || valueProps.length === 0) {
    throw new Error('No value propositions available from MSP');
  }

  // Select the first value proposition
  const valuePropId = valueProps[0].id;
  return valuePropId;
}

// Check if user is authenticated
export function isAuthenticated() {
  return sessionToken !== undefined && authenticatedUserProfile !== null;
}

// Get authenticated user profile
export function getUserProfile() {
  return authenticatedUserProfile;
}

// Clear auth session
export function clearSession() {
  sessionToken = undefined;
  authenticatedUserProfile = null;

  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(SESSION_TOKEN_KEY);
    sessionStorage.removeItem(USER_PROFILE_KEY);
  }
}

// Check if an error is a 401 auth error
export function isAuthError(error) {
  return error?.status === 401 || error?.response?.status === 401;
}

// Reset MSP connection
export function disconnectMsp() {
  mspClientInstance = null;
  clearSession();
}
