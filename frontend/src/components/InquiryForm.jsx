import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useForm } from 'react-hook-form';
import { leadAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function InquiryForm({ coach, onClose, onSuccess }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await leadAPI.createInquiry({
        coach_id: coach.id,
        lead_info: {
          first_name: data.firstName,
          last_name: data.lastName,
          email: data.email,
          phone: data.phone,
          timeframe: data.timeframe,
          financing_status: data.financingStatus,
        },
        message: data.message,
        preferred_contact_method: data.contactMethod,
      });
      onSuccess();
    } catch (error) {
      toast.error('Failed to send inquiry. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Transition appear show={true} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-lg font-medium leading-6 text-gray-900 flex items-center justify-between"
                >
                  Request Information
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </Dialog.Title>

                <div className="mt-2 mb-4">
                  <p className="text-sm text-gray-600">
                    Interested in the {coach.year} {coach.converter} {coach.model}? 
                    Fill out this form and we'll get back to you shortly.
                  </p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="label">First Name *</label>
                      <input
                        type="text"
                        {...register('firstName', { required: 'First name is required' })}
                        className="input-field"
                      />
                      {errors.firstName && (
                        <p className="text-red-500 text-xs mt-1">{errors.firstName.message}</p>
                      )}
                    </div>
                    <div>
                      <label className="label">Last Name *</label>
                      <input
                        type="text"
                        {...register('lastName', { required: 'Last name is required' })}
                        className="input-field"
                      />
                      {errors.lastName && (
                        <p className="text-red-500 text-xs mt-1">{errors.lastName.message}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="label">Email *</label>
                    <input
                      type="email"
                      {...register('email', {
                        required: 'Email is required',
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: 'Invalid email address',
                        },
                      })}
                      className="input-field"
                    />
                    {errors.email && (
                      <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="label">Phone</label>
                    <input
                      type="tel"
                      {...register('phone')}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="label">Purchase Timeframe</label>
                    <select {...register('timeframe')} className="input-field">
                      <option value="">Select timeframe</option>
                      <option value="immediate">Immediate (within 30 days)</option>
                      <option value="3_months">1-3 months</option>
                      <option value="6_months">3-6 months</option>
                      <option value="planning">Just researching</option>
                    </select>
                  </div>

                  <div>
                    <label className="label">Financing</label>
                    <select {...register('financingStatus')} className="input-field">
                      <option value="">Select financing status</option>
                      <option value="cash">Cash purchase</option>
                      <option value="pre_approved">Pre-approved for financing</option>
                      <option value="need_financing">Need financing assistance</option>
                    </select>
                  </div>

                  <div>
                    <label className="label">Message</label>
                    <textarea
                      {...register('message')}
                      rows={3}
                      className="input-field"
                      placeholder="Any specific questions about this coach?"
                    />
                  </div>

                  <div>
                    <label className="label">Preferred Contact Method</label>
                    <select {...register('contactMethod')} className="input-field">
                      <option value="email">Email</option>
                      <option value="phone">Phone</option>
                    </select>
                  </div>

                  <div className="mt-6 flex gap-3">
                    <button
                      type="button"
                      className="btn-secondary flex-1"
                      onClick={onClose}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn-primary flex-1"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Sending...' : 'Send Inquiry'}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
