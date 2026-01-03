#!/usr/bin/env python3
"""
Minimal test to check Firebase JavaScript injection
"""
import streamlit as st
import json

def test_firebase_js():
    """Test Firebase JavaScript injection"""
    st.title("🔧 Firebase JavaScript Test")

    # Simple Firebase config
    firebase_config = {
        "apiKey": "test-api-key",
        "authDomain": "test.firebaseapp.com",
        "projectId": "test-project",
    }

    # Simplified Firebase JavaScript
    firebase_auth_js = f"""
    <script>
        console.log('🔄 Starting Firebase Auth setup...');

        // Show loading indicator
        var loadingDiv = document.createElement('div');
        loadingDiv.id = 'firebase-loading';
        loadingDiv.style.cssText = 'position: fixed; top: 10px; right: 10px; background: #2196F3; color: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; z-index: 1000;';
        loadingDiv.textContent = '🔄 Loading Firebase...';
        document.body.appendChild(loadingDiv);

        console.log('✅ JavaScript executed successfully!');
        loadingDiv.textContent = '✅ JS Working';
        loadingDiv.style.background = '#4CAF50';
        setTimeout(function() {{ loadingDiv.remove(); }}, 3000);
    </script>
    """

    st.markdown("### Test Results:")
    st.markdown("Check browser console for Firebase messages. If you see '🔄 Starting Firebase Auth setup...' and '✅ JavaScript executed successfully!', then JavaScript injection is working.")

    # Inject the JavaScript
    st.markdown(firebase_auth_js, unsafe_allow_html=True)

    st.markdown("---")
    st.info("🔧 If you don't see console messages, there might be an issue with JavaScript injection in Streamlit.")

if __name__ == "__main__":
    test_firebase_js()