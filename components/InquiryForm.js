import { useState } from "react";

const initialForm = {
  name: "",
  email: "",
  company: "",
  message: "",
};

export default function InquiryForm({ productName }) {
  const [form, setForm] = useState(initialForm);
  const [submitted, setSubmitted] = useState(false);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  function submitInquiry(event) {
    event.preventDefault();

    console.log({
      ...form,
      productName,
    });

    setSubmitted(true);
    setForm(initialForm);
  }

  return (
    <form className="inquiry-form" onSubmit={submitInquiry}>
      <div className="form-grid">
        <label>
          <span>Name</span>
          <input
            name="name"
            type="text"
            value={form.name}
            onChange={updateField}
            required
          />
        </label>

        <label>
          <span>Email</span>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={updateField}
            required
          />
        </label>
      </div>

      <label>
        <span>Company</span>
        <input
          name="company"
          type="text"
          value={form.company}
          onChange={updateField}
          required
        />
      </label>

      <label>
        <span>Product name</span>
        <input type="text" value={productName} readOnly />
      </label>

      <label>
        <span>Message</span>
        <textarea
          name="message"
          rows="5"
          value={form.message}
          onChange={updateField}
          required
        />
      </label>

      <button className="button primary" type="submit">
        Send inquiry
      </button>

      {submitted ? (
        <p className="form-status" role="status">
          Inquiry logged. The form is ready for another request.
        </p>
      ) : null}
    </form>
  );
}
