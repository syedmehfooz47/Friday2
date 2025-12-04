# -*- coding: utf-8 -*-
"""
Website Generator - Creates polished, complete HTML websites
Features: Internet research, modern CSS, responsive design, animations
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv
from .logger import Logger
from .llm_handler import llm_handler

load_dotenv()

# Check for Tavily (internet search)
TAVILY_AVAILABLE = False
try:
    from tavily import TavilyClient
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if tavily_api_key:
        tavily_client = TavilyClient(api_key=tavily_api_key)
        TAVILY_AVAILABLE = True
        Logger.log("Tavily available for website research.", "WEBGEN")
except ImportError:
    Logger.log("Tavily not installed. Website generation will work without internet research.", "WARNING")


class WebsiteGenerator:
    """
    Advanced HTML Website Generator with internet research capabilities.
    Creates polished, responsive, modern websites.
    """
    
    # Modern CSS Framework (embedded for standalone HTML)
    MODERN_CSS = """
    /* CSS Reset & Base */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #ec4899;
        --accent: #14b8a6;
        --background: #0f172a;
        --surface: #1e293b;
        --surface-light: #334155;
        --text: #f8fafc;
        --text-muted: #94a3b8;
        --success: #22c55e;
        --warning: #f59e0b;
        --error: #ef4444;
        --gradient: linear-gradient(135deg, var(--primary), var(--secondary));
        --shadow: 0 10px 40px rgba(0,0,0,0.3);
        --shadow-sm: 0 4px 15px rgba(0,0,0,0.2);
        --radius: 12px;
        --radius-lg: 20px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    html { scroll-behavior: smooth; }
    
    body {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: var(--background);
        color: var(--text);
        line-height: 1.6;
        min-height: 100vh;
        overflow-x: hidden;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 1rem;
    }
    h1 { font-size: clamp(2.5rem, 5vw, 4rem); }
    h2 { font-size: clamp(2rem, 4vw, 3rem); }
    h3 { font-size: clamp(1.5rem, 3vw, 2rem); }
    
    p { margin-bottom: 1rem; color: var(--text-muted); }
    a { color: var(--primary); text-decoration: none; transition: var(--transition); }
    a:hover { color: var(--secondary); }
    
    /* Container */
    .container {
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }
    
    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.875rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border: none;
        border-radius: var(--radius);
        cursor: pointer;
        transition: var(--transition);
        text-decoration: none;
    }
    .btn-primary {
        background: var(--gradient);
        color: white;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(99, 102, 241, 0.5);
    }
    .btn-secondary {
        background: var(--surface);
        color: var(--text);
        border: 1px solid var(--surface-light);
    }
    .btn-secondary:hover {
        background: var(--surface-light);
        border-color: var(--primary);
    }
    
    /* Cards */
    .card {
        background: var(--surface);
        border-radius: var(--radius-lg);
        padding: 2rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid rgba(255,255,255,0.05);
        transition: var(--transition);
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* Navigation */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding: 1rem 0;
    }
    .navbar .container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .nav-brand {
        font-size: 1.5rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .nav-links {
        display: flex;
        gap: 2rem;
        list-style: none;
    }
    .nav-links a {
        color: var(--text-muted);
        font-weight: 500;
        position: relative;
    }
    .nav-links a:hover { color: var(--text); }
    .nav-links a::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 0;
        height: 2px;
        background: var(--gradient);
        transition: var(--transition);
    }
    .nav-links a:hover::after { width: 100%; }
    
    /* Hero Section */
    .hero {
        min-height: 100vh;
        display: flex;
        align-items: center;
        padding: 8rem 0 4rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 30%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 70% 70%, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
        animation: rotate 30s linear infinite;
    }
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .hero-content {
        position: relative;
        z-index: 1;
        max-width: 800px;
    }
    .hero-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 50px;
        font-size: 0.875rem;
        color: var(--primary);
        margin-bottom: 1.5rem;
    }
    .hero-title {
        margin-bottom: 1.5rem;
    }
    .hero-title span {
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    /* Sections */
    .section {
        padding: 6rem 0;
        position: relative;
    }
    .section-header {
        text-align: center;
        max-width: 600px;
        margin: 0 auto 4rem;
    }
    .section-tag {
        color: var(--primary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    /* Grid */
    .grid {
        display: grid;
        gap: 2rem;
    }
    .grid-2 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .grid-3 { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
    .grid-4 { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
    
    /* Features */
    .feature-icon {
        width: 60px;
        height: 60px;
        border-radius: var(--radius);
        background: var(--gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Stats */
    .stats {
        display: flex;
        gap: 4rem;
        justify-content: center;
        flex-wrap: wrap;
        padding: 3rem 0;
    }
    .stat {
        text-align: center;
    }
    .stat-value {
        font-size: 3rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label {
        color: var(--text-muted);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Testimonials */
    .testimonial {
        text-align: center;
        padding: 2rem;
    }
    .testimonial-text {
        font-size: 1.25rem;
        font-style: italic;
        color: var(--text);
        margin-bottom: 1.5rem;
    }
    .testimonial-author {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    .testimonial-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        background: var(--surface);
        padding: 4rem 0 2rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .footer-grid {
        display: grid;
        grid-template-columns: 2fr repeat(3, 1fr);
        gap: 4rem;
        margin-bottom: 3rem;
    }
    .footer-brand {
        font-size: 1.5rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    .footer-links h4 {
        color: var(--text);
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    .footer-links ul {
        list-style: none;
    }
    .footer-links li {
        margin-bottom: 0.5rem;
    }
    .footer-links a {
        color: var(--text-muted);
        font-size: 0.875rem;
    }
    .footer-bottom {
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        color: var(--text-muted);
        font-size: 0.875rem;
    }
    
    /* Contact Form */
    .form-group {
        margin-bottom: 1.5rem;
    }
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .form-input {
        width: 100%;
        padding: 1rem;
        background: var(--background);
        border: 1px solid var(--surface-light);
        border-radius: var(--radius);
        color: var(--text);
        font-size: 1rem;
        transition: var(--transition);
    }
    .form-input:focus {
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    textarea.form-input {
        min-height: 150px;
        resize: vertical;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .animate-fadeInUp {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .animate-float {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .nav-links { display: none; }
        .hero { text-align: center; }
        .hero-buttons { justify-content: center; }
        .footer-grid { grid-template-columns: 1fr; text-align: center; }
        .stats { gap: 2rem; }
    }
    
    /* Utilities */
    .text-center { text-align: center; }
    .text-gradient {
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    .mb-4 { margin-bottom: 2rem; }
    .mt-4 { margin-top: 2rem; }
    .py-2 { padding-top: 1rem; padding-bottom: 1rem; }
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.output_folder = self.project_root / "Data" / "GeneratedWebsites"
        self.output_folder.mkdir(parents=True, exist_ok=True)
        Logger.log(f"WebsiteGenerator initialized. Output: {self.output_folder}", "WEBGEN")
    
    def _research_topic(self, topic: str, website_type: str) -> Dict[str, Any]:
        """Research topic using internet to gather relevant information"""
        research_data = {
            "topic_info": "",
            "features": [],
            "content_ideas": [],
            "industry_terms": [],
            "competitors": []
        }
        
        if not TAVILY_AVAILABLE:
            Logger.log("Tavily not available, using LLM for content generation only", "WEBGEN")
            return research_data
        
        try:
            # Search for topic information
            Logger.log(f"Researching '{topic}' for {website_type} website...", "WEBGEN")
            
            search_queries = [
                f"{topic} {website_type} website best practices",
                f"{topic} key features and benefits",
                f"modern {topic} industry trends 2024"
            ]
            
            all_results = []
            for query in search_queries[:2]:  # Limit to 2 searches
                try:
                    result = tavily_client.search(query=query, max_results=3)
                    if result and 'results' in result:
                        all_results.extend(result['results'])
                except Exception as e:
                    Logger.log(f"Search query failed: {e}", "WARNING")
            
            # Extract useful information
            if all_results:
                content_snippets = [r.get('content', '')[:500] for r in all_results[:5]]
                research_data["topic_info"] = "\n".join(content_snippets)
                Logger.log(f"Gathered research data from {len(all_results)} sources", "WEBGEN")
            
        except Exception as e:
            Logger.log(f"Research failed: {e}", "WARNING")
        
        return research_data
    
    def _generate_content_with_llm(self, topic: str, website_type: str, research_data: Dict, sections: list) -> Dict[str, str]:
        """Use LLM to generate polished website content"""
        
        research_context = research_data.get("topic_info", "")
        
        prompt = f"""Generate complete, professional website content for a {website_type} website about "{topic}".

{f'RESEARCH CONTEXT (use this for accuracy):{chr(10)}{research_context}' if research_context else ''}

Generate content for these sections: {', '.join(sections)}

Requirements:
- Professional, engaging, and persuasive copy
- Include specific details, numbers, and facts where appropriate
- Write compelling headlines and subheadings
- Include call-to-action text
- Make it sound premium and trustworthy
- Include 3-4 key features/benefits with descriptions
- Include 3 testimonials with names
- Include statistics/numbers that look realistic

Return as JSON with this structure:
{{
    "brand_name": "Creative brand name for the website",
    "tagline": "Short catchy tagline",
    "hero_title": "Main headline (can include HTML for emphasis)",
    "hero_description": "2-3 sentence description",
    "features": [
        {{"icon": "emoji", "title": "Feature 1", "description": "Description"}},
        {{"icon": "emoji", "title": "Feature 2", "description": "Description"}},
        {{"icon": "emoji", "title": "Feature 3", "description": "Description"}}
    ],
    "stats": [
        {{"value": "10K+", "label": "Stat label"}},
        {{"value": "99%", "label": "Stat label"}},
        {{"value": "24/7", "label": "Stat label"}}
    ],
    "about_title": "About section title",
    "about_text": "About section paragraph",
    "testimonials": [
        {{"text": "Quote", "author": "Name", "role": "Title"}},
        {{"text": "Quote", "author": "Name", "role": "Title"}}
    ],
    "cta_title": "Call to action headline",
    "cta_text": "CTA description",
    "footer_description": "Brief company/site description"
}}

Return ONLY valid JSON, no markdown or extra text."""

        try:
            response = llm_handler.generate(prompt)
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                content = json.loads(json_match.group())
                Logger.log("Successfully generated website content with LLM", "WEBGEN")
                return content
        except json.JSONDecodeError as e:
            Logger.log(f"JSON parse error: {e}", "WARNING")
        except Exception as e:
            Logger.log(f"LLM generation error: {e}", "WARNING")
        
        # Fallback content
        return self._get_fallback_content(topic, website_type)
    
    def _get_fallback_content(self, topic: str, website_type: str) -> Dict[str, str]:
        """Fallback content if LLM fails"""
        topic_title = topic.title()
        return {
            "brand_name": topic_title,
            "tagline": f"Your Premier {topic_title} Solution",
            "hero_title": f"Welcome to <span>{topic_title}</span>",
            "hero_description": f"Discover the best {topic.lower()} experience. We provide premium solutions tailored to your needs.",
            "features": [
                {"icon": "⚡", "title": "Fast & Efficient", "description": f"Experience lightning-fast {topic.lower()} services."},
                {"icon": "🛡️", "title": "Secure & Reliable", "description": "Your security is our top priority."},
                {"icon": "🎯", "title": "Precision Focus", "description": "Targeted solutions for maximum impact."}
            ],
            "stats": [
                {"value": "10K+", "label": "Happy Customers"},
                {"value": "99%", "label": "Satisfaction Rate"},
                {"value": "24/7", "label": "Support Available"}
            ],
            "about_title": f"About {topic_title}",
            "about_text": f"We are passionate about delivering exceptional {topic.lower()} experiences. Our team of experts works tirelessly to ensure you get the best service possible.",
            "testimonials": [
                {"text": "Absolutely amazing service! Exceeded all expectations.", "author": "John Smith", "role": "CEO"},
                {"text": "The best decision we ever made. Highly recommended!", "author": "Sarah Johnson", "role": "Marketing Director"}
            ],
            "cta_title": "Ready to Get Started?",
            "cta_text": "Join thousands of satisfied customers today.",
            "footer_description": f"Your trusted partner for all things {topic.lower()}."
        }
    
    def _build_html(self, content: Dict, website_type: str, include_sections: list) -> str:
        """Build the complete HTML document"""
        
        brand = content.get("brand_name", "Brand")
        
        # Build navigation
        nav_items = []
        if "hero" in include_sections: nav_items.append('<a href="#home">Home</a>')
        if "features" in include_sections: nav_items.append('<a href="#features">Features</a>')
        if "about" in include_sections: nav_items.append('<a href="#about">About</a>')
        if "testimonials" in include_sections: nav_items.append('<a href="#testimonials">Testimonials</a>')
        if "contact" in include_sections: nav_items.append('<a href="#contact">Contact</a>')
        
        nav_html = f"""
    <nav class="navbar">
        <div class="container">
            <a href="#" class="nav-brand">{brand}</a>
            <ul class="nav-links">
                {''.join(f'<li>{item}</li>' for item in nav_items)}
            </ul>
            <a href="#contact" class="btn btn-primary">Get Started</a>
        </div>
    </nav>"""
        
        # Build hero section
        hero_html = ""
        if "hero" in include_sections:
            hero_html = f"""
    <section class="hero" id="home">
        <div class="container">
            <div class="hero-content animate-fadeInUp">
                <span class="hero-badge">✨ {content.get('tagline', 'Welcome')}</span>
                <h1 class="hero-title">{content.get('hero_title', 'Welcome')}</h1>
                <p style="font-size: 1.25rem; max-width: 600px;">{content.get('hero_description', '')}</p>
                <div class="hero-buttons">
                    <a href="#contact" class="btn btn-primary">Get Started →</a>
                    <a href="#features" class="btn btn-secondary">Learn More</a>
                </div>
            </div>
        </div>
    </section>"""
        
        # Build stats section
        stats_html = ""
        if "stats" in include_sections and content.get("stats"):
            stats_items = "".join(f'''
                <div class="stat">
                    <div class="stat-value">{s.get('value', '0')}</div>
                    <div class="stat-label">{s.get('label', '')}</div>
                </div>''' for s in content.get("stats", []))
            stats_html = f"""
    <section class="section" style="background: var(--surface);">
        <div class="container">
            <div class="stats">{stats_items}</div>
        </div>
    </section>"""
        
        # Build features section
        features_html = ""
        if "features" in include_sections and content.get("features"):
            feature_cards = "".join(f'''
                <div class="card">
                    <div class="feature-icon">{f.get('icon', '⭐')}</div>
                    <h3>{f.get('title', 'Feature')}</h3>
                    <p>{f.get('description', '')}</p>
                </div>''' for f in content.get("features", []))
            features_html = f"""
    <section class="section" id="features">
        <div class="container">
            <div class="section-header">
                <p class="section-tag">Features</p>
                <h2>Why Choose Us</h2>
                <p>Discover what makes us the preferred choice</p>
            </div>
            <div class="grid grid-3">{feature_cards}</div>
        </div>
    </section>"""
        
        # Build about section
        about_html = ""
        if "about" in include_sections:
            about_html = f"""
    <section class="section" id="about" style="background: var(--surface);">
        <div class="container">
            <div class="grid grid-2" style="align-items: center; gap: 4rem;">
                <div>
                    <p class="section-tag">About Us</p>
                    <h2>{content.get('about_title', 'About Us')}</h2>
                    <p style="font-size: 1.1rem;">{content.get('about_text', '')}</p>
                    <a href="#contact" class="btn btn-primary mt-4">Learn More</a>
                </div>
                <div class="card animate-float" style="background: var(--gradient); padding: 3rem; text-align: center;">
                    <h3 style="font-size: 2rem; color: white;">🚀</h3>
                    <p style="color: white; font-size: 1.25rem; margin: 0;">Innovation & Excellence</p>
                </div>
            </div>
        </div>
    </section>"""
        
        # Build testimonials section
        testimonials_html = ""
        if "testimonials" in include_sections and content.get("testimonials"):
            testimonial_cards = "".join(f'''
                <div class="card testimonial">
                    <p class="testimonial-text">"{t.get('text', '')}"</p>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">{t.get('author', 'A')[0]}</div>
                        <div>
                            <strong>{t.get('author', 'Anonymous')}</strong>
                            <p style="margin: 0; font-size: 0.875rem;">{t.get('role', '')}</p>
                        </div>
                    </div>
                </div>''' for t in content.get("testimonials", []))
            testimonials_html = f"""
    <section class="section" id="testimonials">
        <div class="container">
            <div class="section-header">
                <p class="section-tag">Testimonials</p>
                <h2>What People Say</h2>
                <p>Hear from our satisfied customers</p>
            </div>
            <div class="grid grid-2">{testimonial_cards}</div>
        </div>
    </section>"""
        
        # Build CTA section
        cta_html = ""
        if "cta" in include_sections:
            cta_html = f"""
    <section class="section" style="background: var(--gradient);">
        <div class="container text-center">
            <h2 style="color: white;">{content.get('cta_title', 'Ready to Get Started?')}</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.25rem; max-width: 600px; margin: 0 auto 2rem;">{content.get('cta_text', '')}</p>
            <a href="#contact" class="btn" style="background: white; color: var(--primary);">Get Started Now →</a>
        </div>
    </section>"""
        
        # Build contact section
        contact_html = ""
        if "contact" in include_sections:
            contact_html = f"""
    <section class="section" id="contact">
        <div class="container">
            <div class="grid grid-2" style="gap: 4rem;">
                <div>
                    <p class="section-tag">Contact</p>
                    <h2>Get In Touch</h2>
                    <p>Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.</p>
                    <div class="mt-4">
                        <p><strong>📧 Email:</strong> contact@{brand.lower().replace(' ', '')}.com</p>
                        <p><strong>📱 Phone:</strong> +1 (555) 123-4567</p>
                        <p><strong>📍 Address:</strong> 123 Business Street, City, Country</p>
                    </div>
                </div>
                <div class="card">
                    <form>
                        <div class="form-group">
                            <label class="form-label">Name</label>
                            <input type="text" class="form-input" placeholder="Your name">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-input" placeholder="your@email.com">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Message</label>
                            <textarea class="form-input" placeholder="Your message..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%;">Send Message</button>
                    </form>
                </div>
            </div>
        </div>
    </section>"""
        
        # Build footer
        footer_html = f"""
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <div class="footer-brand">{brand}</div>
                    <p>{content.get('footer_description', '')}</p>
                </div>
                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="#home">Home</a></li>
                        <li><a href="#features">Features</a></li>
                        <li><a href="#about">About</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </div>
                <div class="footer-links">
                    <h4>Legal</h4>
                    <ul>
                        <li><a href="#">Privacy Policy</a></li>
                        <li><a href="#">Terms of Service</a></li>
                        <li><a href="#">Cookie Policy</a></li>
                    </ul>
                </div>
                <div class="footer-links">
                    <h4>Connect</h4>
                    <ul>
                        <li><a href="#">Twitter</a></li>
                        <li><a href="#">LinkedIn</a></li>
                        <li><a href="#">Instagram</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© {datetime.now().year} {brand}. All rights reserved. Made with ❤️</p>
            </div>
        </div>
    </footer>"""
        
        # Combine everything
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{content.get('hero_description', '')}">
    <title>{brand} - {content.get('tagline', '')}</title>
    <style>{self.MODERN_CSS}</style>
</head>
<body>
{nav_html}
{hero_html}
{stats_html}
{features_html}
{about_html}
{testimonials_html}
{cta_html}
{contact_html}
{footer_html}

    <script>
        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
        
        // Navbar scroll effect
        window.addEventListener('scroll', () => {{
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {{
                navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            }} else {{
                navbar.style.background = 'rgba(15, 23, 42, 0.8)';
            }}
        }});
        
        // Animation on scroll
        const observerOptions = {{ threshold: 0.1 }};
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);
        
        document.querySelectorAll('.card').forEach(card => {{
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'all 0.6s ease-out';
            observer.observe(card);
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def generate(
        self,
        topic: str,
        website_type: str = "landing",
        use_internet: bool = True,
        sections: list = None
    ) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """
        Generate a complete, polished HTML website.
        
        Args:
            topic: The topic/subject of the website
            website_type: Type of website (landing, portfolio, business, blog, product)
            use_internet: Whether to research online for better content
            sections: List of sections to include (default: all)
        
        Returns:
            Tuple of (message, file_path, stats)
        """
        username = os.getenv("Username", "Boss")
        
        # Default sections
        if sections is None:
            sections = ["hero", "stats", "features", "about", "testimonials", "cta", "contact"]
        
        Logger.log(f"Generating {website_type} website about '{topic}'", "WEBGEN")
        
        try:
            # Step 1: Research (if enabled)
            research_data = {}
            if use_internet and TAVILY_AVAILABLE:
                research_data = self._research_topic(topic, website_type)
            
            # Step 2: Generate content with LLM
            content = self._generate_content_with_llm(topic, website_type, research_data, sections)
            
            # Step 3: Build HTML
            html = self._build_html(content, website_type, sections)
            
            # Step 4: Save file
            safe_topic = re.sub(r'[^\w\s-]', '', topic).replace(' ', '_')[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_topic}_{website_type}_{timestamp}.html"
            output_path = self.output_folder / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            file_size = output_path.stat().st_size
            
            stats = {
                "topic": topic,
                "type": website_type,
                "sections": sections,
                "file_size": file_size,
                "file_size_formatted": f"{file_size / 1024:.1f} KB",
                "researched": bool(research_data.get("topic_info")),
                "brand_name": content.get("brand_name", topic)
            }
            
            Logger.log(f"Website generated: {output_path} ({stats['file_size_formatted']})", "WEBGEN")
            
            return f"Created a polished {website_type} website for '{topic}', Boss. File: {filename}", str(output_path), stats
            
        except Exception as e:
            Logger.log(f"Website generation failed: {e}", "ERROR")
            import traceback
            Logger.log(traceback.format_exc(), "ERROR")
            return f"Website generation failed: {e}", None, {}


# Global instance
website_generator = WebsiteGenerator()
