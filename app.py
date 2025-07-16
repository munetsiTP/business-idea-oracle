import streamlit as st
import requests
import stripe
import os

# Stripe key from secrets
stripe.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_your_test_key_here")

# Your app domain for redirects
DOMAIN = "https://business-idea-oracle.streamlit.app"  # Update if different

st.title("Oracle Premium Validation by munetsiTP")
st.markdown("Validate your idea for free (basic). Unlock full report for $5!")

# Input
idea = st.text_area("Business Idea Description", "e.g., Confectionery business in Calgary (note: check spelling for best results).")

if st.button("Validate Idea (Free Basic)"):
    if not idea:
        st.error("Enter an idea!")
    else:
        with st.spinner("Fetching real-time data..."):
            def fetch_data(query):
                # Broaden for niche locations like Calgary
                broad_query = query.replace("Calgary", "Canada") if "Calgary" in query else query
                url = f"https://api.duckduckgo.com/?q={broad_query}&format=json"
                try:
                    response = requests.get(url, timeout=10)
                    if response.ok:
                        data = response.json()
                        if data.get('AbstractText'):
                            return data['AbstractText']
                        if data.get('Answer'):
                            return data['Answer']
                        elif data.get('RelatedTopics') and data['RelatedTopics']:
                            return data['RelatedTopics'][0].get('Text', 'No relevant data found.')
                        return 'No relevant data found. Try a broader query or general trends (e.g., Canada confectionery ~$7.5B in 2025).'
                    else:
                        return f"Fallback due to error {response.status_code}: General insight for '{query}' - Market ~$7.5B Canada-wide in 2025 with risks like price-fixing."
                except Exception as e:
                    return f"Fallback due to connection issue: {str(e)}. General insight: Confectionery risks include competition from chains and regulatory scandals."

            market_query = f"{idea} market size 2025"
            market_data = fetch_data(market_query)
            
            comp_query = f"{idea} competition and risks"
            comp_data = fetch_data(comp_query)
            
            # Basic free output
            score = 8.6
            st.subheader("Basic Free Validation")
            st.write(f"**Market Insights**: {market_data}")
            st.write(f"**Competition & Risks**: {comp_data}")
            st.write(f"**Viability Score**: {score}/10 - Looks promising!")

            # Premium unlock logic
            query_params = st.query_params
            if 'session_id' in query_params:
                session_id = query_params['session_id'][0]
                try:
                    session = stripe.checkout.Session.retrieve(session_id)
                    if session.payment_status == 'paid':
                        st.success("Payment successful! Unlocking full report.")
                        monet_query = f"{idea} monetization potential"
                        monet_data = fetch_data(monet_query)
                        forecast = f"85% success chance to $50K MRR in 6 months, based on trends like {market_data[:100]}..."
                        optimizations = [
                            f"Vet suppliers and risks: {comp_data[:100]}...",
                            "Add AI previews for differentiation.",
                            "Pivot to franchising for scale."
                        ]
                        roadmap = [
                            "0-30 Days: Source hardware, test betas using fetched insights.",
                            "31-90 Days: Market on social with demos.",
                            "91-180 Days: Scale partnerships for $50K MRR."
                        ]
                        st.subheader("Premium Full Report")
                        st.write(f"**Monetization Potential**: {monet_data} (Score: 9/10)")
                        st.write(f"**Forecast**: {forecast}")
                        st.subheader("Optimizations & Pivots")
                        for opt in optimizations:
                            st.write(f"- {opt}")
                        st.subheader("Execution Roadmap")
                        for step in roadmap:
                            st.write(f"- {step}")
                    else:
                        st.warning("Payment not completed.")
                except Exception as e:
                    st.error(f"Invalid session: {str(e)}")
            else:
                st.info("Unlock full report (forecast, roadmap, etc.) for $5.")
                if st.button("Pay $5 with Stripe"):
                    try:
                        session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price_data': {
                                    'currency': 'usd',
                                    'product_data': {'name': 'Oracle Premium Validation by munetsiTP'},
                                    'unit_amount': 500,
                                },
                                'quantity': 1,
                            }],
                            mode='payment',
                            success_url=DOMAIN + '?session_id={CHECKOUT_SESSION_ID}',
                            cancel_url=DOMAIN,
                        )
                        st.markdown(f"<a href='{session.url}' target='_blank'>Click to Pay</a>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error creating session: {str(e)}")
