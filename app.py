import streamlit as st
import pandas as pd
import io
from etl.loader import load_file, get_sample
from etl.schema_agent import detect_schema
from etl.quality_agent import analyze_quality
from etl.codegen_agent import run_codegen
from etl.report_agent import generate_report
from etl.normalize_agent import run_normalization

st.set_page_config(
    page_title="AI Smart ETL Pipeline",
    page_icon="⚙️",
    layout="wide"
)
st.title("AI Smart ETL Pipeline")
st.caption("Upload any messy CSV or Excel — AI detects schema, fixes issues, and generates cleaning code automatically")

uploaded = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "xls"])

if uploaded:
    df = load_file(uploaded)
    st.success(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    with st.expander("Raw data preview"):
        st.dataframe(df.head(20), use_container_width=True)

    if st.button("Run AI ETL Pipeline", type="primary"):

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Pipeline progress")
            s1 = st.empty(); s1.markdown("⬜ Schema detection")
            s2 = st.empty(); s2.markdown("⬜ Quality analysis")
            s3 = st.empty(); s3.markdown("⬜ Semantic normalization")
            s4 = st.empty(); s4.markdown("⬜ Code generation")
            s5 = st.empty(); s5.markdown("⬜ Report generation")
            score_box = st.empty()
            

        with col2:
            output_area = st.empty()
            output_area.info("Pipeline running...")

        # Stage 1 — Schema
        s1.markdown("🔄 Detecting schema...")
        sample = get_sample(df)
        schema = detect_schema(sample)
        s1.markdown("✅ Schema detected")

        with col2:
            output_area.empty()
            st.subheader("Detected schema")
            if schema and "error" not in schema[0]:
                schema_df = pd.DataFrame(schema)
                st.dataframe(schema_df, use_container_width=True)
            else:
                st.warning("Schema detection had issues — continuing with defaults")

        # Stage 2 — Quality
        s2.markdown("🔄 Analyzing quality...")
        quality = analyze_quality(df, schema)
        s2.markdown("✅ Quality analyzed")

        severity = quality.get("severity", "unknown")
        score = quality.get("confidence_score", 0)
        color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(severity, "⚪")
        score_box.metric("Data quality score", f"{score}/100", delta=f"{color} {severity} severity")

        with st.expander("Quality issues found"):
            st.markdown(f"**{quality.get('summary', '')}**")
            issues = quality.get("issues", [])
            for issue in issues:
                st.markdown(
                    f"- **{issue.get('issue')}** "
                    f"→ {issue.get('affected_columns')} "
                    f"— Fix: {issue.get('fix_strategy')}"
                )

        # Stage 3 — Semantic normalization
        s3.markdown("🔄 Normalizing inconsistent values...")
        normalized_df, norm_code, norm_status = run_normalization(df)
        s3.markdown("✅ Normalization complete" if norm_status == "success" else "⚠️ Normalization had issues")

        with st.expander("Normalization code generated"):
            st.code(norm_code, language="python")
            if norm_status != "success":
                st.error(norm_status)

        before_unique = {col: df[col].nunique() for col in df.select_dtypes("object").columns}
        after_unique = {col: normalized_df[col].nunique() for col in normalized_df.select_dtypes("object").columns}

        with st.expander("Normalization results"):
            for col in before_unique:
                before = before_unique[col]
                after = after_unique.get(col, before)
                if before != after:
                    st.markdown(f"**{col}**: {before} unique values → {after} unique values (−{before-after})")
                    
        # Stage 4 — Code gen
        s4.markdown("🔄 Generating cleaning code...")
        cleaned_df, code, status = run_codegen(normalized_df, schema, quality)
        s4.markdown("✅ Code generated and executed" if status == "success" else "⚠️ Code executed with issues")

        with st.expander("Generated Pandas code"):
            st.code(code, language="python")
            if status != "success":
                st.error(status)

        # Stage 4 — Report
        s5.markdown("🔄 Generating report...")
        report = generate_report(normalized_df, cleaned_df, schema, quality, code, status)
        s5.markdown("✅ Report ready")

        # Final output
        st.divider()
        st.subheader("Cleaned dataset")
        st.dataframe(cleaned_df.head(50), use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Original rows", df.shape[0])
        col_b.metric("Cleaned rows", cleaned_df.shape[0])
        col_c.metric("Rows removed", df.shape[0] - cleaned_df.shape[0])

        st.subheader("Data quality report")
        st.markdown(report)

        # Download buttons
        st.divider()
        col_d, col_e = st.columns(2)

        with col_d:
            csv = cleaned_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download cleaned CSV",
                csv,
                "cleaned_data.csv",
                "text/csv",
                type="primary"
            )

        with col_e:
            report_bytes = report.encode("utf-8")
            st.download_button(
                "Download quality report",
                report_bytes,
                "quality_report.md",
                "text/markdown"
            )