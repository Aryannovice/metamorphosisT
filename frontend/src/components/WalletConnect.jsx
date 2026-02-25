// WalletConnect Component - DataHaven Wallet Connection UI
import React from 'react';
import { Wallet, Link, Shield, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useDataHaven } from '../context/DataHavenContext';

export default function WalletConnect() {
  const {
    walletAddress,
    walletBalance,
    mspConnected,
    authenticated,
    isConnecting,
    error,
    fullConnect,
    disconnect,
    clearError,
  } = useDataHaven();

  const truncateAddress = (addr) => {
    if (!addr) return '';
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const handleConnect = async () => {
    clearError();
    try {
      await fullConnect();
    } catch (err) {
      console.error('Connection failed:', err);
    }
  };

  // Not connected state
  if (!walletAddress) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Wallet className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">DataHaven Storage</h3>
            <p className="text-xs text-gray-500">Blockchain-verified audit proofs</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        <button
          onClick={handleConnect}
          disabled={isConnecting}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isConnecting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Connecting...
            </>
          ) : (
            <>
              <Wallet className="w-4 h-4" />
              Connect MetaMask
            </>
          )}
        </button>

        <p className="text-xs text-gray-400 text-center mt-3">
          Connect to DataHaven Testnet to store verifiable audit proofs
        </p>
      </div>
    );
  }

  // Connected state
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
            <CheckCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">DataHaven Connected</h3>
            <p className="text-xs text-gray-500">Ready to store proofs on-chain</p>
          </div>
        </div>
      </div>

      {/* Connection Status */}
      <div className="space-y-3 mb-4">
        {/* Wallet */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-green-600" />
            <span className="text-sm text-gray-700">Wallet</span>
          </div>
          <div className="text-right">
            <p className="text-sm font-mono text-gray-900">{truncateAddress(walletAddress)}</p>
            {walletBalance && (
              <p className="text-xs text-gray-500">{walletBalance} MOCK</p>
            )}
          </div>
        </div>

        {/* MSP Connection */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Link className="w-4 h-4 text-green-600" />
            <span className="text-sm text-gray-700">Storage Provider</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${mspConnected ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <span className="text-xs text-gray-600">{mspConnected ? 'Connected' : 'Pending'}</span>
          </div>
        </div>

        {/* Authentication */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-green-600" />
            <span className="text-sm text-gray-700">Authentication</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${authenticated ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <span className="text-xs text-gray-600">{authenticated ? 'SIWE Verified' : 'Pending'}</span>
          </div>
        </div>
      </div>

      {/* Network Info */}
      <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg mb-4">
        <p className="text-xs text-blue-800 font-medium mb-1">DataHaven Testnet</p>
        <p className="text-xs text-blue-600">Chain ID: 55931 • Currency: MOCK</p>
      </div>

      {/* Disconnect Button */}
      <button
        onClick={disconnect}
        className="w-full py-2 px-4 text-gray-600 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 transition-colors"
      >
        Disconnect
      </button>
    </div>
  );
}
