export default function ContactPage() {
  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-display font-bold text-gray-900 mb-8">Contact Us</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h2 className="text-2xl font-semibold mb-4">Get in Touch</h2>
            <p className="text-gray-600 mb-6">
              Have questions about a specific coach or need assistance with your search? 
              Our team of luxury coach experts is here to help.
            </p>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium">Phone</h3>
                <p className="text-gray-600">1-800-PREVOST</p>
              </div>
              <div>
                <h3 className="font-medium">Email</h3>
                <p className="text-gray-600">info@prevostgo.com</p>
              </div>
              <div>
                <h3 className="font-medium">Hours</h3>
                <p className="text-gray-600">Monday - Friday: 9:00 AM - 6:00 PM EST</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-100 p-8 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Send a Message</h2>
            <form className="space-y-4">
              <div>
                <label className="label">Name</label>
                <input type="text" className="input-field" />
              </div>
              <div>
                <label className="label">Email</label>
                <input type="email" className="input-field" />
              </div>
              <div>
                <label className="label">Message</label>
                <textarea className="input-field" rows="4"></textarea>
              </div>
              <button type="submit" className="btn-primary w-full">
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
